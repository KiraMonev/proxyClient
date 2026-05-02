<template>
  <v-card class="pa-6" width="450" rounded="xl" elevation="4" color="surface">
    <v-card-title class="text-h5 text-center mb-4 text-primary">
      Вход
    </v-card-title>

    <v-alert
      v-if="errorMessage"
      type="error"
      variant="tonal"
      class="mb-4"
      rounded="lg"
    >
      {{ errorMessage }}
    </v-alert>

    <v-form @submit.prevent="handleLogin" :disabled="loading">
      <v-text-field
        v-model="email"
        label="Email"
        type="email"
        prepend-inner-icon="mdi-email-outline"
        variant="outlined"
        rounded="lg"
        class="mb-2"
        :rules="[rules.required]"
      />

      <v-text-field
        v-model="password"
        label="Пароль"
        type="password"
        prepend-inner-icon="mdi-lock-outline"
        variant="outlined"
        rounded="lg"
        class="mb-4"
        :rules="[rules.required]"
      />

      <v-btn
        type="submit"
        block
        size="large"
        color="primary"
        rounded="lg"
        :loading="loading"
      >
        Войти
      </v-btn>
    </v-form>

    <v-card-text class="text-center mt-4">
      Нет аккаунта?
      <router-link to="/register" class="text-primary">Зарегистрироваться</router-link>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

const rules = {
  required: (v) => !!v || 'Обязательное поле',
}

async function handleLogin() {
  loading.value = true
  errorMessage.value = ''

  try {
    await authStore.login(email.value, password.value)
    router.push('/profile')
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Неверный email или пароль'
  } finally {
    loading.value = false
  }
}
</script>
