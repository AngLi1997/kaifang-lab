<template>
  <AppPage :show-footer="false">
    <main class="login-page">
      <section class="login-card">
        <div class="login-brand">
          <img :src="logoUrl" alt="" />
          <h1>{{ $t('app_name') }}</h1>
        </div>

        <form class="login-form" @submit.prevent="handleLogin">
          <h2 class="login-form__heading">{{ $t('views.login.heading') }}</h2>

          <label class="login-field">
            <span>{{ $t('views.login.label_username') }}</span>
            <n-input
              v-model:value="loginInfo.username"
              autofocus
              size="large"
              :placeholder="$t('views.login.placeholder_username')"
              :maxlength="20"
            />
          </label>
          <label class="login-field">
            <span>{{ $t('views.login.label_password') }}</span>
            <n-input
              v-model:value="loginInfo.password"
              size="large"
              type="password"
              show-password-on="mousedown"
              :placeholder="$t('views.login.placeholder_password')"
              :maxlength="128"
            />
          </label>

          <n-button
            class="login-submit"
            size="large"
            type="primary"
            :loading="loading"
            attr-type="submit"
          >
            {{ $t('views.login.text_login') }}
          </n-button>
          <p class="login-form__note">{{ $t('views.login.security_note') }}</p>
        </form>
      </section>
    </main>
  </AppPage>
</template>

<script setup>
import { lStorage, setToken } from '@/utils'
import api from '@/api'
import { addDynamicRoutes } from '@/router'
import { useI18n } from 'vue-i18n'
const logoUrl = '/favicon.png'

const router = useRouter()
const { query } = useRoute()
const { t } = useI18n({ useScope: 'global' })

const loginInfo = ref({
  username: '',
  password: '',
})

initLoginInfo()

function initLoginInfo() {
  const localLoginInfo = lStorage.get('loginInfo')
  if (localLoginInfo) {
    loginInfo.value.username = localLoginInfo.username || ''
    loginInfo.value.password = localLoginInfo.password || ''
  }
}

const loading = ref(false)
async function handleLogin() {
  const { username, password } = loginInfo.value
  if (!username || !password) {
    $message.warning(t('views.login.message_input_username_password'))
    return
  }
  try {
    loading.value = true
    $message.loading(t('views.login.message_verifying'))
    const res = await api.login({ username, password: password.toString() })
    $message.success(t('views.login.message_login_success'))
    setToken(res.data.access_token)
    await addDynamicRoutes()
    if (query.redirect) {
      const path = query.redirect
      console.log('path', { path, query })
      Reflect.deleteProperty(query, 'redirect')
      router.push({ path, query })
    } else {
      router.push('/')
    }
  } catch (e) {
    console.error('login error', e.error)
  }
  loading.value = false
}
</script>

<style scoped lang="scss">
.login-page {
  display: flex;
  min-height: 100%;
  flex: 1;
  align-items: center;
  justify-content: center;
  overflow: auto;
  padding: 40px 28px;
  background: radial-gradient(ellipse at 12% 12%, rgba(143, 36, 40, 0.055), transparent 36%),
    linear-gradient(135deg, #f5f3f0 0%, #efeeeb 100%);
}

.login-card {
  display: grid;
  width: min(1080px, 100%);
  grid-template-columns: 1.05fr 0.85fr;
  overflow: hidden;
  margin: auto;
  border: 1px solid #e6e0dc;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 18px 55px rgba(48, 37, 33, 0.07);
}

.login-brand {
  display: flex;
  min-height: 520px;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 58px 60px;
  background: linear-gradient(145deg, #faf8f6 0%, #f3efeb 100%);
}

.login-brand img {
  width: 96px;
  height: 96px;
  border-radius: 12px;
}

.login-brand h1 {
  margin: 0;
  color: #282525;
  font-size: clamp(36px, 4vw, 52px);
  font-weight: 700;
  letter-spacing: 0.02em;
}

.login-form {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 58px 54px;
}

.login-form__heading {
  margin: 0 0 30px;
  color: #282525;
  font-size: 24px;
  font-weight: 650;
}

.login-field {
  display: grid;
  gap: 9px;
  margin-bottom: 20px;
  color: #504a47;
  font-size: 13px;
  font-weight: 600;
}

.login-submit {
  width: 100%;
  margin-top: 6px;
}

.login-form__note {
  margin: 15px 0 0;
  color: #8b8581;
  font-size: 12px;
  line-height: 1.7;
  text-align: center;
}

@media (max-width: 760px) {
  .login-page {
    padding: 24px 16px;
  }

  .login-card {
    grid-template-columns: 1fr;
  }

  .login-brand {
    min-height: 0;
    gap: 16px;
    padding: 32px 28px;
  }

  .login-brand img {
    width: 56px;
    height: 56px;
  }

  .login-brand h1 {
    font-size: 30px;
  }

  .login-form {
    padding: 32px 28px;
  }

  .login-form__heading {
    margin-bottom: 22px;
  }
}
</style>
