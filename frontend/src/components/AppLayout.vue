<template>
  <v-app-bar color="surface" elevation="1" density="comfortable">
    <v-app-bar-title>
      <span class="text-primary font-weight-bold">Proxy</span>
      <span class="text-on-surface">Service</span>
    </v-app-bar-title>

    <template v-slot:append>
      <template v-if="authStore.isAuthenticated">
        <v-btn to="/profile" variant="text" prepend-icon="mdi-account">
          Кабинет
        </v-btn>
        <v-btn variant="text" prepend-icon="mdi-logout" @click="handleLogout">
          Выйти
        </v-btn>
      </template>
      <template v-else>
        <v-btn to="/login" variant="text" prepend-icon="mdi-login">
          Вход
        </v-btn>
        <v-btn to="/register" variant="text" prepend-icon="mdi-account-plus">
          Регистрация
        </v-btn>
      </template>
    </template>
  </v-app-bar>

  <v-main>
    <v-container fluid class="d-flex align-center justify-center" style="min-height: calc(100vh - 64px);">
      <slot />
    </v-container>
  </v-main>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
