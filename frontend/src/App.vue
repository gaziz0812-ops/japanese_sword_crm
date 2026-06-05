<script setup>
import { onMounted, ref } from 'vue'

// ref создает реактивный список товаров: когда список изменится, Vue обновит экран.
const products = ref([])

// ref хранит состояние загрузки, чтобы показать пользователю, что данные еще едут с backend.
const isLoading = ref(true)

// ref хранит текст ошибки, если запрос к Django API не получится.
const errorMessage = ref('')

// onMounted запускает код после того, как компонент появился на странице.
onMounted(async () => {
  try {
    // fetch делает HTTP GET-запрос к публичному API товаров Django.
    const response = await fetch('http://127.0.0.1:8000/api/products/')

    // Если backend вернул не 200 OK, считаем это ошибкой.
    if (!response.ok) {
      throw new Error('Не удалось загрузить товары')
    }

    // response.json() превращает JSON-ответ backend в JavaScript-объекты.
    const data = await response.json()
    products.value = data.results
  } catch (error) {
    // Если запрос упал, сохраняем сообщение ошибки для вывода на экран.
    errorMessage.value = error.message
  } finally {
    // finally сработает и при успехе, и при ошибке: загрузка завершена.
    isLoading.value = false
  }
})
</script>

<template>
  <main class="page">
    <header class="header">
      <p class="eyebrow">Japanese Sword</p>
      <h1>Каталог</h1>
    </header>

    <p v-if="isLoading">Загружаем товары...</p>
    <p v-else-if="errorMessage">{{ errorMessage }}</p>

    <section v-else class="product-grid">
      <article v-for="product in products" :key="product.id" class="product-card">
        <img v-if="product.image" :src="product.image" :alt="product.name" class="product-image">

        <div class="product-body">
          <p class="sku">Арт. {{ product.sku }}</p>
          <h2>{{ product.name }}</h2>
          <p class="price">{{ product.sale_price }} руб.</p>
          <p class="stock">{{ product.stock_status }}</p>
        </div>
      </article>
    </section>
  </main>
</template>