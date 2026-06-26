# Архитектура проекта Japanese Sword CRM / ERP

Документ описывает, как устроен проект на уровне модулей, моделей, бизнес-процессов и потоков данных.

Главная мысль архитектуры: система разделяет **заявку клиента**, **факт продажи**, **складские движения**, **партии товара** и **отчеты**. Благодаря этому заказ можно редактировать до оплаты, продажа фиксируется как исторический факт, а остатки и прибыль считаются из событий, а не из ручных полей.

## Контекст системы

```mermaid
flowchart TD
    customer["Клиент в Telegram"] --> mini_app["Telegram Mini App<br/>Vue + Vite"]
    mini_app --> api["Публичный API<br/>Django REST Framework"]
    api --> django["Django backend<br/>бизнес-логика"]
    django --> db["SQLite<br/>текущая БД разработки"]

    admin_user["Администратор"] --> admin_panel["Django Admin"]
    admin_panel --> django

    django --> telegram_api["Telegram Bot API"]
    telegram_api --> customer
    telegram_api --> admin_user

    django --> reports["Отчеты и аналитика<br/>Django Admin"]
```

### Что здесь важно

- Клиент работает не с Django Admin, а с Telegram Mini App.
- Mini App ходит в backend через REST API.
- Администратор работает через Django Admin.
- Telegram Bot API используется для уведомлений и запуска Mini App.
- Все критичные бизнес-операции проходят через Django backend.

## Django-приложения

```mermaid
flowchart LR
    manufacturers["manufacturers<br/>производители"]
    products["products<br/>каталог товаров"]
    supplies["supplies<br/>поставки"]
    stock["stock<br/>склад и партии"]
    orders["orders<br/>заказы"]
    sales["sales<br/>продажи и возвраты"]
    users["users<br/>пользователи и Telegram ID"]
    reports["reports<br/>аналитика"]
    bot["telegram_bot<br/>бот"]

    manufacturers --> products
    products --> supplies
    products --> stock
    products --> orders
    products --> sales
    users --> orders
    users --> sales
    supplies --> stock
    orders --> sales
    sales --> stock
    stock --> reports
    orders --> reports
    sales --> reports
    bot --> orders
```

## Основные модели и связи

```mermaid
classDiagram
    class Manufacturer {
        name
        contacts
        notes
    }

    class Product {
        sku
        name
        sale_price
        is_active
        stock_balance
    }

    class User {
        username
        telegram_id
        role
    }

    class Supply {
        supply_date
        yuan_rate
        cargo_commission_percent
        total_shipping_cost
        total_package_weight
    }

    class SupplyItem {
        quantity
        price_yuan
        china_shipping_yuan
        calculated_unit_cost
    }

    class ManualSupply {
        supply_date
        comment
    }

    class ManualSupplyItem {
        quantity
        unit_cost
        cost_note
    }

    class StockMovement {
        product
        movement_type
        quantity
        source_type
        source_id
    }

    class StockBatch {
        product
        quantity
        remaining_quantity
        unit_cost
        source_type
        source_id
    }

    class Order {
        customer
        customer_name
        telegram_username
        status
        total_amount
        paid_at
        shipped_at
        tracking_number
    }

    class OrderItem {
        product
        quantity
        discount_percent
        unit_price
        unit_price_after_discount
        total_price
    }

    class Sale {
        product
        customer
        order
        order_item
        quantity
        unit_sale_price
        total_sale_amount
        cost_price
        profit
    }

    class SaleCostAllocation {
        sale
        stock_batch
        quantity
        unit_cost
        total_cost
    }

    class SaleReturn {
        order
        sale
        quantity
        refund_amount
        destination
    }

    class StockWriteOff {
        product
        quantity
        reason
    }

    class StockReservation {
        product
        quantity
        status
    }

    Manufacturer "1" --> "*" Product
    Product "1" --> "*" SupplyItem
    Product "1" --> "*" ManualSupplyItem
    Product "1" --> "*" StockMovement
    Product "1" --> "*" StockBatch
    Product "1" --> "*" OrderItem
    Product "1" --> "*" Sale
    Product "1" --> "*" StockWriteOff
    Product "1" --> "*" StockReservation

    User "1" --> "*" Order
    User "1" --> "*" Sale

    Supply "1" --> "*" SupplyItem
    ManualSupply "1" --> "*" ManualSupplyItem

    Order "1" --> "*" OrderItem
    Order "1" --> "*" Sale
    OrderItem "1" --> "0..1" Sale

    Sale "1" --> "*" SaleCostAllocation
    StockBatch "1" --> "*" SaleCostAllocation
    Sale "1" --> "*" SaleReturn
    Order "1" --> "*" SaleReturn
```

## Почему Order и Sale разделены

`Order` - это заказ или заявка клиента.

Он появляется, когда клиент оформил корзину в Mini App или когда администратор вручную создал заказ в админке.

`Order` сам не списывает склад. До оплаты заказ может меняться: клиент может добавить товар, убрать позицию, попросить скидку или изменить состав заказа.

`Sale` - это факт оплаченной продажи.

Он появляется после подтверждения оплаты и действия "Провести продажу". Именно `Sale`:

- списывает товар со склада;
- запускает FIFO;
- создает движение склада;
- фиксирует себестоимость;
- фиксирует прибыль;
- становится основанием для возврата.

Разделение нужно, чтобы не путать "клиент хочет купить" и "товар реально продан".

## Поток заказа

```mermaid
sequenceDiagram
    participant C as Клиент
    participant F as Telegram Mini App
    participant A as DRF API
    participant O as Order
    participant Admin as Администратор
    participant S as Sale
    participant Stock as Склад
    participant T as Telegram Bot

    C->>F: Выбирает товары
    F->>A: POST /api/orders/
    A->>O: Создает Order и OrderItem
    A->>T: Уведомление администратору
    T-->>Admin: Новый заказ
    Admin->>O: Проверяет заказ и оплату
    Admin->>O: Ставит статус "Оплачен"
    Admin->>O: Действие "Провести продажу"
    O->>S: Создает Sale по позициям заказа
    S->>Stock: FIFO-списание партий
    Stock-->>S: Себестоимость продажи
    S->>Stock: Движение склада "Продажа"
    Admin->>O: Добавляет трек-номер
    O->>T: Уведомление клиенту
    T-->>C: Заказ отправлен
```

## Складская архитектура

```mermaid
flowchart TD
    supply_item["SupplyItem / ManualSupplyItem"] --> inbound["StockMovement: INBOUND"]
    supply_item --> batch["StockBatch<br/>партия товара"]

    sale["Sale"] --> allocation["SaleCostAllocation<br/>из каких партий списали"]
    allocation --> batch
    sale --> sale_movement["StockMovement: SALE"]

    sale_return["SaleReturn"] --> return_movement["StockMovement: RETURN"]
    sale_return --> writeoff_return["StockMovement: WRITE_OFF<br/>если возврат списан"]
    sale_return --> batch_restore["Возврат в партии<br/>если товар вернули на продажу"]

    writeoff["StockWriteOff"] --> writeoff_alloc["StockWriteOffAllocation"]
    writeoff_alloc --> batch
    writeoff --> writeoff_movement["StockMovement: WRITE_OFF"]

    reservation["StockReservation"] --> reservation_alloc["StockReservationAllocation"]
    reservation_alloc --> batch
    reservation --> reserve_movement["StockMovement: RESERVE"]
    reservation --> unreserve_movement["StockMovement: UNRESERVE"]
```

### Почему остаток считается через StockMovement

Остаток товара - это не самостоятельное поле в `Product`.

Остаток считается как результат истории:

```text
приход + возврат + снятие резерва - продажа - списание - резерв
```

Такой подход делает склад проверяемым. Если остаток изменился, можно открыть журнал движений и увидеть, какая операция на него повлияла.

## FIFO

FIFO используется, чтобы себестоимость продажи считалась по старым партиям в первую очередь.

Пример:

```text
Партия 1: 5 шт. по 1000 руб.
Партия 2: 5 шт. по 1300 руб.

Продажа: 6 шт.

FIFO:
- 5 шт. списываются из партии 1;
- 1 шт. списывается из партии 2.
```

В проекте это фиксируется через `SaleCostAllocation`.

`SaleCostAllocation` хранит:

- какая продажа списала товар;
- из какой партии;
- сколько штук;
- по какой себестоимости;
- какая общая себестоимость списания.

Это нужно для корректной прибыли и возвратов.

## Возвраты

Возврат оформляется по продаже.

`SaleReturn` знает:

- к какому заказу относится возврат;
- по какой продаже оформляется возврат;
- сколько товара возвращается;
- какая сумма возвращается клиенту;
- куда определить товар: вернуть на продажу или списать.

Если товар возвращается на продажу, система возвращает количество в те партии, из которых товар был продан.

Если товар списывается, система создает дополнительное складское движение `WRITE_OFF`.

Защита: нельзя вернуть больше, чем было продано и еще не возвращено.

## Резервы и списания

`StockWriteOff` используется, когда товар окончательно выбыл: брак, повреждение, потеря, недостача.

`StockReservation` используется, когда товар временно нельзя продавать, но он не уничтожен и не списан.

Разница:

```text
Списание - товар окончательно ушел со склада.
Резерв - товар временно убран из доступного остатка.
```

Резерв можно снять. Списание нельзя удалить или откатить напрямую.

## API-архитектура

```mermaid
flowchart LR
    mini_app["Vue Mini App"] --> products_api["GET /api/products/"]
    mini_app --> product_detail["GET /api/products/{id}/"]
    mini_app --> create_order["POST /api/orders/"]
    mini_app --> my_orders["GET /api/orders/my/"]

    products_api --> product_serializer["ProductPublicSerializer"]
    product_detail --> product_detail_serializer["ProductDetailSerializer"]
    create_order --> order_create_serializer["OrderCreateSerializer"]
    my_orders --> order_history_serializer["OrderHistorySerializer"]
```

Публичный API отдает только то, что нужно клиенту.

Он не должен отдавать:

- себестоимость;
- прибыль;
- контакты производителей;
- внутренние комментарии;
- партии товара;
- служебные складские движения.

## Telegram-контур

```mermaid
flowchart TD
    user["Telegram user"] --> bot["Telegram bot"]
    bot --> mini_app["Открывает Mini App"]
    mini_app --> initdata["Передает initData"]
    initdata --> backend["Django backend"]
    backend --> validate["Проверка initData"]
    validate --> user_model["User<br/>telegram_id + username"]
    user_model --> order["Order.customer"]
    backend --> notify_admin["Уведомление админу"]
    backend --> notify_client["Уведомление клиенту"]
```

Telegram ID нужен не для красоты. Он связывает реального Telegram-пользователя с заказами в базе.

Это позволяет:

- показывать клиенту его историю заказов;
- отправлять уведомления конкретному пользователю;
- не просить клиента вручную вводить Telegram ID;
- защищаться от подмены данных через initData.

## Админка

Django Admin в проекте - это не просто техническая панель.

Это рабочее место администратора:

- каталог товаров;
- поставки;
- ручные поставки;
- партии;
- движения склада;
- заказы;
- продажи;
- возвраты;
- резервы;
- списания;
- отчеты.

Некоторые разделы админки являются журналами и защищены от ручного вмешательства.

Например, продажа создается через заказ, а не вручную. Складское движение создается операциями, а не редактируется руками.

## Отчеты

Отчеты читают данные из заказов, продаж, возвратов, товаров и склада.

Они не создают бизнес-событий, а только показывают состояние системы:

- сколько продано;
- сколько возвращено;
- какая чистая выручка;
- какая прибыль;
- какие товары продаются лучше;
- какие товары заканчиваются;
- сколько товара лежит на складе в розничных ценах.

## Где проходят деньги

```mermaid
flowchart TD
    product_price["Product.sale_price<br/>текущая цена товара"] --> order_item["OrderItem.unit_price<br/>цена на момент заказа"]
    order_item --> order_total["Order.total_amount<br/>сумма заказа"]
    order_item --> sale_price["Sale.unit_sale_price<br/>цена продажи"]
    sale_price --> sale_total["Sale.total_sale_amount<br/>выручка продажи"]

    batch_cost["StockBatch.unit_cost<br/>себестоимость партии"] --> allocation_cost["SaleCostAllocation.total_cost<br/>себестоимость списания"]
    allocation_cost --> profit["Sale.profit<br/>прибыль"]
    sale_total --> profit
```

Цена товара в каталоге может измениться.

Поэтому заказ и продажа фиксируют исторические цены, чтобы старые продажи не пересчитывались задним числом.

## Точки расширения

### PostgreSQL

Сейчас используется SQLite. Следующий взрослый шаг - PostgreSQL.

Это не меняет бизнес-логику, потому что Django ORM изолирует большую часть работы с БД, но делает проект ближе к production.

### Docker

Docker Compose нужен, чтобы запускать проект одинаково на разных машинах:

- backend;
- PostgreSQL;
- frontend;
- telegram bot.

### Тесты

Первые тесты стоит писать не на все подряд, а на самую дорогую бизнес-логику:

- FIFO-списание;
- запрет продажи сверх остатка;
- запрет возврата сверх продажи;
- проведение продажи только из оплаченного заказа;
- публичный API не отдает внутренние поля.

### Celery и Redis

Сейчас они не обязательны.

Они станут полезны, если:

- Telegram-уведомления нужно отправлять в фоне;
- появится тяжелый импорт Excel;
- появятся регулярные задачи;
- HTTP-запросы нельзя будет задерживать внешними API.

### Логирование

Минимальное логирование стоит добавить для:

- создания заказа;
- проведения продажи;
- ошибок Telegram-уведомлений;
- критичных складских операций.

## Как объяснять проект на презентации

Короткий вариант:

> Это CRM/ERP-система для продаж через Telegram. Клиент оформляет заказ в Telegram Mini App, администратор подтверждает оплату в Django Admin, система проводит продажу, списывает склад по FIFO, считает себестоимость и прибыль, а затем показывает аналитику по продажам и остаткам.

Сильные технические места:

- разделение `Order` и `Sale`;
- склад через журнал движений;
- FIFO через партии и allocation-модели;
- защита от ручного нарушения бизнес-логики;
- Telegram Mini App + проверка initData;
- отчеты в админке;
- исторические цены и себестоимость.

