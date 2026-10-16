<template>
  <AppPage :show-footer="false">
    <main class="workbench">
      <section class="workbench-greeting">
        <span class="workbench-greeting__accent" aria-hidden="true"></span>
        <h1>{{ greeting }}</h1>
        <img class="workbench-greeting__mark" src="/favicon.png" alt="" aria-hidden="true" />
      </section>
    </main>
  </AppPage>
</template>

<script setup>
import { useUserStore } from '@/store'
import { useI18n } from 'vue-i18n'

const { t } = useI18n({ useScope: 'global' })
const userStore = useUserStore()

const now = ref(new Date())
let timer
onMounted(() => {
  timer = setInterval(() => {
    now.value = new Date()
  }, 60 * 1000)
})
onBeforeUnmount(() => clearInterval(timer))

/** Maps the local hour to a greeting period: 5–8 / 8–11 / 11–13 / 13–18 / 18–5. */
function greetingKey(hour) {
  if (hour >= 5 && hour < 8) return 'greeting_early_morning'
  if (hour >= 8 && hour < 11) return 'greeting_morning'
  if (hour >= 11 && hour < 13) return 'greeting_noon'
  if (hour >= 13 && hour < 18) return 'greeting_afternoon'
  return 'greeting_evening'
}

const greeting = computed(() =>
  t(`views.workbench.${greetingKey(now.value.getHours())}`, { username: userStore.nickname })
)
</script>

<style scoped lang="scss">
.workbench {
  display: flex;
  width: 100%;
  max-width: 1320px;
  min-height: 100%;
  margin: 0 auto;
  padding: 12px 4px 28px;
}

.workbench-greeting {
  position: relative;
  display: flex;
  min-height: 420px;
  flex: 1;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
  padding: 56px 64px;
  border: 1px solid #e8e2de;
  border-radius: 8px;
  background: radial-gradient(ellipse at 88% 20%, rgba(143, 36, 40, 0.06), transparent 42%),
    linear-gradient(120deg, #fff 0%, #faf7f4 55%, #f3efeb 100%);
}

.workbench-greeting::before,
.workbench-greeting::after {
  position: absolute;
  border: 1px solid rgba(143, 36, 40, 0.09);
  border-radius: 50%;
  content: '';
}

.workbench-greeting::before {
  right: -120px;
  bottom: -160px;
  width: 460px;
  height: 460px;
}

.workbench-greeting::after {
  right: -40px;
  bottom: -80px;
  width: 300px;
  height: 300px;
}

.workbench-greeting__accent {
  width: 36px;
  height: 3px;
  margin-bottom: 24px;
  border-radius: 2px;
  background: #8f2428;
}

.workbench-greeting h1 {
  position: relative;
  z-index: 1;
  margin: 0;
  color: #282525;
  font-size: clamp(30px, 4vw, 48px);
  font-weight: 650;
  letter-spacing: 0.02em;
  line-height: 1.35;
  word-break: break-word;
}

.workbench-greeting__mark {
  position: absolute;
  right: 72px;
  bottom: 64px;
  width: 88px;
  height: 88px;
  border-radius: 10px;
  opacity: 0.12;
}

@media (max-width: 760px) {
  .workbench-greeting {
    min-height: 260px;
    padding: 36px 28px;
  }

  .workbench-greeting__accent {
    margin-bottom: 18px;
  }

  .workbench-greeting h1 {
    font-size: 28px;
  }

  .workbench-greeting__mark {
    right: 28px;
    bottom: 28px;
    width: 56px;
    height: 56px;
  }
}
</style>
