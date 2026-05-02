<template>
  <v-card class="pa-6" width="550" rounded="xl" elevation="4" color="surface">
    <v-card-title class="text-h5 text-center mb-6 text-primary">
      Личный кабинет
    </v-card-title>

    <!-- Alerts -->
    <v-alert
      v-if="successMessage"
      type="success"
      variant="tonal"
      class="mb-4"
      rounded="lg"
      closable
      @click:close="successMessage = ''"
    >
      {{ successMessage }}
    </v-alert>

    <v-alert
      v-if="errorMessage"
      type="error"
      variant="tonal"
      class="mb-4"
      rounded="lg"
      closable
      @click:close="errorMessage = ''"
    >
      {{ errorMessage }}
    </v-alert>

    <!-- Loading -->
    <div v-if="loadingProfile" class="d-flex justify-center my-6">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <!-- Profile Info -->
    <template v-else-if="profile">
      <v-list bg-color="surface-variant" rounded="lg" class="mb-6">
        <v-list-item prepend-icon="mdi-email-outline">
          <v-list-item-title class="text-body-1">{{ profile.email }}</v-list-item-title>
          <v-list-item-subtitle>Email</v-list-item-subtitle>
        </v-list-item>

        <v-divider />

        <v-list-item prepend-icon="mdi-key-outline">
          <v-list-item-title class="text-body-1 font-weight-medium" style="font-family: monospace;">
            {{ profile.activation_key || '—' }}
          </v-list-item-title>
          <v-list-item-subtitle>Ключ активации</v-list-item-subtitle>
        </v-list-item>

        <v-divider />

        <v-list-item prepend-icon="mdi-calendar-outline">
          <v-list-item-title class="text-body-1">
            {{ new Date(profile.created_at).toLocaleDateString('ru-RU') }}
          </v-list-item-title>
          <v-list-item-subtitle>Дата регистрации</v-list-item-subtitle>
        </v-list-item>
      </v-list>

      <!-- Refresh Key Button -->
      <v-btn
        block
        color="secondary"
        rounded="lg"
        size="large"
        class="mb-6"
        prepend-icon="mdi-refresh"
        :loading="refreshingKey"
        @click="handleRefreshKey"
      >
        Обновить ключ
      </v-btn>

      <!-- Change Password Section -->
      <v-expansion-panels variant="accordion" rounded="lg">
        <v-expansion-panel color="surface-variant">
          <v-expansion-panel-title>
            <v-icon class="mr-2">mdi-lock-reset</v-icon>
            Сменить пароль
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <v-form @submit.prevent="handleChangePassword" :disabled="changingPassword">
              <v-text-field
                v-model="oldPassword"
                label="Текущий пароль"
                type="password"
                variant="outlined"
                rounded="lg"
                density="compact"
                class="mb-2"
              />
              <v-text-field
                v-model="newPassword"
                label="Новый пароль"
                type="password"
                variant="outlined"
                rounded="lg"
                density="compact"
                class="mb-2"
                :rules="[v => (v && v.length >= 6) || 'Минимум 6 символов']"
              />
              <v-text-field
                v-model="newPasswordConfirm"
                label="Подтвердите новый пароль"
                type="password"
                variant="outlined"
                rounded="lg"
                density="compact"
                class="mb-3"
                :rules="[v => v === newPassword || 'Пароли не совпадают']"
              />
              <v-btn
                type="submit"
                block
                color="primary"
                rounded="lg"
                :loading="changingPassword"
              >
                Сменить пароль
              </v-btn>
            </v-form>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </template>
  </v-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/client'

const profile = ref(null)
const loadingProfile = ref(true)
const refreshingKey = ref(false)
const changingPassword = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const oldPassword = ref('')
const newPassword = ref('')
const newPasswordConfirm = ref('')

async function loadProfile() {
  loadingProfile.value = true
  try {
    const response = await api.get('/api/profile')
    profile.value = response.data
  } catch (err) {
    errorMessage.value = 'Не удалось загрузить профиль'
  } finally {
    loadingProfile.value = false
  }
}

async function handleRefreshKey() {
  refreshingKey.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await api.post('/api/profile/refresh-key')
    successMessage.value = response.data.message
    await loadProfile()
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Ошибка обновления ключа'
  } finally {
    refreshingKey.value = false
  }
}

async function handleChangePassword() {
  if (newPassword.value !== newPasswordConfirm.value) {
    errorMessage.value = 'Пароли не совпадают'
    return
  }

  changingPassword.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await api.post('/api/profile/change-password', {
      old_password: oldPassword.value,
      new_password: newPassword.value,
      new_password_confirm: newPasswordConfirm.value,
    })
    successMessage.value = response.data.message
    oldPassword.value = ''
    newPassword.value = ''
    newPasswordConfirm.value = ''
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Ошибка смены пароля'
  } finally {
    changingPassword.value = false
  }
}

onMounted(loadProfile)
</script>
