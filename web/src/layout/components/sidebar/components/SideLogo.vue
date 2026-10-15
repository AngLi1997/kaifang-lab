<template>
  <router-link class="brand-lockup" to="/" :aria-label="title">
    <img class="brand-lockup__logo" :src="logoUrl" alt="" />
    <h2 v-show="!appStore.collapsed" class="brand-lockup__title">{{ title }}</h2>
  </router-link>
</template>

<script setup>
import { useAppStore } from '@/store'

const logoUrl = '/favicon.png'
const title = import.meta.env.VITE_TITLE || 'KaifangLab'

const appStore = useAppStore()
</script>

<style scoped lang="scss">
.brand-lockup {
  display: flex;
  width: 100%;
  height: 60px;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.brand-lockup__logo {
  width: 30px;
  height: 30px;
  flex: none;
  border-radius: 4px;
  object-fit: contain;
}

.brand-lockup__title {
  margin: 0;
  color: var(--primary-color);
  font-size: 16px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: 0.01em;
  white-space: nowrap;
}
</style>
