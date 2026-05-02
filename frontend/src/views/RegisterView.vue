<template>
  <v-card class="pa-6" width="450" rounded="xl" elevation="4" color="surface">
    <v-card-title class="text-h5 text-center mb-4 text-primary">
      Регистрация
    </v-card-title>

    <v-alert
      v-if="successMessage"
      type="success"
      variant="tonal"
      class="mb-4"
      rounded="lg"
    >
      {{ successMessage }}
    </v-alert>

    <v-alert
      v-if="errorMessage"
      type="error"
      variant="tonal"
      class="mb-4"
      rounded="lg"
    >
      {{ errorMessage }}
    </v-alert>

    <v-form @submit.prevent="handleRegister" :disabled="loading">
      <v-text-field
        v-model="email"
        label="Email"
        type="email"
        prepend-inner-icon="mdi-email-outline"
        variant="outlined"
        rounded="lg"
        class="mb-2"
        :rules="[rules.required, rules.email]"
      />

      <v-text-field
        v-model="password"
        label="Пароль"
        type="password"
        prepend-inner-icon="mdi-lock-outline"
        variant="outlined"
        rounded="lg"
        class="mb-2"
        :rules="[rules.required, rules.minLength]"
      />

      <v-text-field
        v-model="passwordConfirm"
        label="Подтвердите пароль"
        type="password"
        prepend-inner-icon="mdi-lock-check-outline"
        variant="outlined"
        rounded="lg"
        class="mb-4"
        :rules="[rules.required, rules.passwordMatch]"
      />

      <v-btn
        type="submit"
        block
        size="large"
        color="primary"
        rounded="lg"
        :loading="loading"
      >
        Зарегистрироваться
      </v-btn>
    </v-form>

    <v-card-text class="text-center mt-4">
      Уже есть аккаунт?
      <router-link to="/login" class="text-primary">Войти</router-link>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const loading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const rules = {
  required: (v) => !!v || 'Обязательное поле',
  email: (v) => /.+@.+\..+/.test(v) || 'Некорректный email',
  minLength: (v) => (v && v.length >= 6) || 'Минимум 6 символов',
  passwordMatch: () => password.value === passwordConfirm.value || 'Пароли не совпадают',
}

async function handleRegister() {
  if (password.value !== passwordConfirm.value) {
    errorMessage.value = 'Пароли не совпадают'
    return
  }

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const result = await authStore.register(email.value, password.value, passwordConfirm.value)
    successMessage.value = result.message
    email.value = ''
    password.value = ''
    passwordConfirm.value = ''
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Ошибка регистрации'
  } finally {
    loading.value = false
  }
}
</script>
