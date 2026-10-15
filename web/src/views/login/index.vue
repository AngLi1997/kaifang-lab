<template>
  <AppPage :show-footer="false">
    <main class="login-page">
      <div class="login-frame">
        <header class="login-brand">
          <div class="login-brand__identity">
            <img :src="logoUrl" alt="" />
            <span>{{ $t('app_name') }}</span>
          </div>
          <span class="login-brand__descriptor">{{ $t('views.login.platform_descriptor') }}</span>
        </header>

        <section class="login-card">
          <div class="login-intro">
            <span class="login-intro__eyebrow">{{ $t('views.login.platform_label') }}</span>
            <h1>{{ $t('views.login.intro_title') }}</h1>
            <p>{{ $t('views.login.intro_description') }}</p>

            <ul class="login-capabilities">
              <li><span>01</span> {{ $t('views.login.capability_identity') }}</li>
              <li><span>02</span> {{ $t('views.login.capability_organization') }}</li>
              <li><span>03</span> {{ $t('views.login.capability_audit') }}</li>
            </ul>
          </div>

          <form class="login-form" @submit.prevent="handleLogin">
            <div class="login-form__heading">
              <span>{{ $t('views.login.entry_label') }}</span>
              <h2>{{ $t('views.login.heading') }}</h2>
              <p>{{ $t('views.login.prompt') }}</p>
            </div>

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

        <footer class="login-footer">
          <span>{{ $t('views.login.footer_brand') }}</span>
          <span>{{ $t('views.login.footer_capabilities') }}</span>
        </footer>
      </div>
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

.login-frame {
  display: flex;
  width: min(1080px, 100%);
  min-height: 560px;
  flex-direction: column;
  justify-content: space-between;
  gap: 28px;
  margin: auto;
}

.login-brand,
.login-brand__identity,
.login-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.login-brand__identity {
  justify-content: flex-start;
  gap: 12px;
  color: #282525;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.login-brand__identity img {
  width: 38px;
  height: 38px;
  border-radius: 5px;
}

.login-brand__descriptor,
.login-intro__eyebrow {
  color: #887d78;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.16em;
}

.login-card {
  display: grid;
  grid-template-columns: 1.05fr 0.85fr;
  overflow: hidden;
  border: 1px solid #e6e0dc;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 18px 55px rgba(48, 37, 33, 0.07);
}

.login-intro {
  position: relative;
  display: flex;
  min-height: 470px;
  flex-direction: column;
  justify-content: center;
  padding: 58px 60px;
  background: linear-gradient(145deg, #faf8f6 0%, #f3efeb 100%);
}

.login-intro::after {
  position: absolute;
  right: 42px;
  bottom: 44px;
  width: 100px;
  height: 100px;
  border: 1px solid rgba(143, 36, 40, 0.1);
  border-radius: 50%;
  content: '';
}

.login-intro__eyebrow {
  color: #8f2428;
}

.login-intro h1 {
  margin: 22px 0 14px;
  color: #282525;
  font-size: clamp(28px, 3vw, 38px);
  font-weight: 650;
  letter-spacing: 0.02em;
  line-height: 1.45;
  white-space: pre-line;
}

.login-intro p {
  max-width: 430px;
  margin: 0;
  color: #716966;
  font-size: 14px;
  line-height: 1.9;
}

.login-capabilities {
  display: grid;
  gap: 17px;
  margin: 42px 0 0;
  padding: 0;
  color: #4e4946;
  font-size: 13px;
  list-style: none;
}

.login-capabilities li {
  display: flex;
  align-items: center;
  gap: 14px;
}

.login-capabilities li span {
  color: #9b7772;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.login-form {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 58px 54px;
}

.login-form__heading {
  margin-bottom: 30px;
}

.login-form__heading > span {
  color: #8f2428;
  font-size: 12px;
  font-weight: 600;
}

.login-form__heading h2 {
  margin: 12px 0 8px;
  color: #282525;
  font-size: 24px;
  font-weight: 650;
}

.login-form__heading p,
.login-form__note {
  margin: 0;
  color: #8b8581;
  font-size: 12px;
  line-height: 1.7;
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
  margin-top: 15px;
  text-align: center;
}

.login-footer {
  color: #8b8581;
  font-size: 11px;
  letter-spacing: 0.02em;
}

@media (max-width: 760px) {
  .login-page {
    padding: 24px 16px;
  }

  .login-frame {
    min-height: 0;
  }

  .login-brand__descriptor,
  .login-intro::after,
  .login-capabilities {
    display: none;
  }

  .login-card {
    grid-template-columns: 1fr;
  }

  .login-intro {
    min-height: 0;
    padding: 30px 28px 26px;
  }

  .login-intro h1 {
    margin: 12px 0 8px;
    font-size: 25px;
  }

  .login-intro p {
    font-size: 12px;
  }

  .login-form {
    padding: 32px 28px;
  }

  .login-form__heading {
    margin-bottom: 22px;
  }

  .login-footer {
    align-items: flex-start;
    flex-direction: column;
    gap: 6px;
  }
}
</style>
