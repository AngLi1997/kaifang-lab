<template>
  <AppPage :show-footer="false">
    <main class="authorize-page">
      <section class="authorize-card">
        <header class="authorize-brand">
          <img :src="logoUrl" alt="" />
          <span>{{ $t('app_name') }}</span>
        </header>

        <template v-if="!callback">
          <h1>{{ $t('views.authorize.invalid_title') }}</h1>
          <p>{{ $t('views.authorize.invalid_description') }}</p>
        </template>
        <template v-else-if="finished">
          <h1>{{ $t('views.authorize.finished_title') }}</h1>
          <p>{{ $t('views.authorize.finished_description') }}</p>
        </template>
        <template v-else>
          <h1>{{ $t('views.authorize.title') }}</h1>
          <p>{{ $t('views.authorize.description') }}</p>
          <div class="authorize-account">
            <img :src="avatarUrl" alt="" />
            <div>
              <strong>{{ displayName || $t('views.authorize.loading') }}</strong>
              <span v-if="user?.email">{{ user.email }}</span>
            </div>
          </div>
          <div class="authorize-actions">
            <n-button size="large" type="primary" :disabled="!user" @click="authorize">
              {{ $t('views.authorize.allow') }}
            </n-button>
            <n-button size="large" @click="deny">{{ $t('views.authorize.deny') }}</n-button>
          </div>
          <p class="authorize-switch">
            {{ $t('views.authorize.not_you') }}
            <a href="#" @click.prevent="switchAccount">{{ $t('views.authorize.switch_account') }}</a>
          </p>
        </template>
      </section>
    </main>
  </AppPage>
</template>

<script setup>
import api from '@/api'
import { getToken, removeToken } from '@/utils'

const logoUrl = '/favicon.png'
const route = useRoute()
const router = useRouter()

/**
 * Accept only a loopback callback so the token never leaves the user's machine.
 * KaifangHarness Desktop listens on 127.0.0.1 with a random port during one sign-in attempt.
 */
function loopbackCallback(value) {
  if (typeof value !== 'string') return null
  try {
    const url = new URL(value)
    const loopback = url.hostname === '127.0.0.1' || url.hostname === 'localhost'
    if (url.protocol !== 'http:' || !loopback || url.pathname !== '/kaifang/callback') return null
    return url
  } catch {
    return null
  }
}

const callback = loopbackCallback(route.query.redirect_uri)
const state = typeof route.query.state === 'string' ? route.query.state : ''
const user = ref(null)
const finished = ref(false)
const displayName = computed(() => user.value?.nickname || user.value?.username || '')
const avatarUrl = computed(() => new URL(user.value?.avatar || logoUrl, window.location.origin).href)

function returnTo(params) {
  const target = new URL(callback.href)
  for (const [key, value] of Object.entries({ ...params, state })) target.searchParams.set(key, value)
  finished.value = true
  window.location.href = target.href
}

function authorize() {
  returnTo({ token: getToken() })
}

function deny() {
  returnTo({ error: 'access_denied' })
}

function switchAccount() {
  removeToken()
  router.replace({ path: '/login', query: { ...route.query, redirect: '/authorize' } })
}

onMounted(async () => {
  if (!callback) return
  const res = await api.getUserInfo()
  user.value = res.data
})
</script>

<style scoped lang="scss">
.authorize-page {
  display: flex;
  min-height: 100%;
  flex: 1;
  align-items: center;
  justify-content: center;
  padding: 40px 16px;
  background: radial-gradient(ellipse at 12% 12%, rgba(143, 36, 40, 0.055), transparent 36%),
    linear-gradient(135deg, #f5f3f0 0%, #efeeeb 100%);
}

.authorize-card {
  width: min(440px, 100%);
  padding: 40px 36px;
  border: 1px solid #e6e0dc;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 18px 55px rgba(48, 37, 33, 0.07);
}

.authorize-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #282525;
  font-size: 16px;
  font-weight: 700;
}

.authorize-brand img {
  width: 30px;
  height: 30px;
  border-radius: 5px;
}

h1 {
  margin: 28px 0 8px;
  color: #282525;
  font-size: 22px;
  font-weight: 650;
}

p {
  margin: 0;
  color: #716966;
  font-size: 13px;
  line-height: 1.8;
}

.authorize-account {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 24px 0;
  padding: 14px 16px;
  border: 1px solid #eee8e4;
  border-radius: 8px;
  background: #faf8f6;
}

.authorize-account img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.authorize-account div {
  display: grid;
  gap: 2px;
  color: #282525;
  font-size: 14px;
}

.authorize-account span {
  color: #8b8581;
  font-size: 12px;
}

.authorize-actions {
  display: grid;
  gap: 12px;
}

.authorize-switch {
  margin-top: 18px;
  text-align: center;
  font-size: 12px;
}

.authorize-switch a {
  color: #8f2428;
}
</style>
