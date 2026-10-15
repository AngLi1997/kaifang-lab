<template>
  <AppPage :show-footer="false">
    <main class="workbench">
      <section class="workbench-hero">
        <div class="workbench-hero__copy">
          <span class="workbench-eyebrow">{{ $t('views.workbench.platform_label') }}</span>
          <h1>{{ $t('views.workbench.title') }}</h1>
          <p>{{ $t('views.workbench.text_welcome') }}</p>
          <div class="workbench-user">
            <img :src="userStore.avatar" alt="" />
            <span>{{ $t('views.workbench.text_hello', { username: userStore.name }) }}</span>
          </div>
        </div>
        <div class="workbench-mark" aria-hidden="true">
          <img src="/favicon.png" alt="" />
          <span>KAIFANGLAB</span>
        </div>
      </section>

      <section class="workbench-capabilities">
        <header class="workbench-section-heading">
          <div>
            <span>{{ $t('views.workbench.label_overview') }}</span>
            <h2>{{ $t('views.workbench.label_capabilities') }}</h2>
          </div>
          <span class="workbench-section-heading__note">KaifangLab · v{{ version }}</span>
        </header>

        <div class="capability-grid">
          <article v-for="item in capabilityData" :key="item.index" class="capability-card">
            <span class="capability-card__index">{{ item.index }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
          </article>
        </div>
      </section>

      <section class="workbench-boundary">
        <span class="workbench-boundary__mark"></span>
        <p>{{ $t('views.workbench.text_boundary') }}</p>
      </section>
    </main>
  </AppPage>
</template>

<script setup>
import { useUserStore } from '@/store'
import { useI18n } from 'vue-i18n'

const { t } = useI18n({ useScope: 'global' })
const version = import.meta.env.VITE_APP_VERSION || '0.1.0'

const capabilityData = computed(() => [
  {
    index: '01',
    title: t('views.workbench.label_identity'),
    description: t('views.workbench.text_identity'),
  },
  {
    index: '02',
    title: t('views.workbench.label_organization'),
    description: t('views.workbench.text_organization'),
  },
  {
    index: '03',
    title: t('views.workbench.label_audit'),
    description: t('views.workbench.text_audit'),
  },
])

const userStore = useUserStore()
</script>

<style scoped lang="scss">
.workbench {
  display: grid;
  max-width: 1320px;
  gap: 22px;
  margin: 0 auto;
  padding: 12px 4px 28px;
}

.workbench-hero {
  display: flex;
  min-height: 230px;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
  padding: 40px 46px;
  border: 1px solid #e8e2de;
  border-radius: 8px;
  background: linear-gradient(110deg, #fff 0%, #fbf8f6 100%);
}

.workbench-hero__copy {
  max-width: 760px;
}

.workbench-eyebrow {
  color: #8f2428;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.16em;
}

.workbench-hero h1 {
  margin: 15px 0 9px;
  color: #2a2725;
  font-size: 28px;
  font-weight: 650;
  letter-spacing: 0.02em;
}

.workbench-hero p {
  max-width: 700px;
  margin: 0;
  color: #706965;
  font-size: 14px;
  line-height: 1.9;
}

.workbench-user {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-top: 24px;
  color: #57514e;
  font-size: 12px;
}

.workbench-user img {
  width: 26px;
  height: 26px;
  border: 1px solid #e9e2dd;
  border-radius: 50%;
  object-fit: cover;
}

.workbench-mark {
  display: flex;
  min-width: 130px;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: #958983;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.16em;
}

.workbench-mark img {
  width: 76px;
  height: 76px;
  border-radius: 8px;
}

.workbench-capabilities {
  padding: 28px 30px 30px;
  border: 1px solid #e8e2de;
  border-radius: 8px;
  background: #fff;
}

.workbench-section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 22px;
}

.workbench-section-heading > div > span {
  color: #8f2428;
  font-size: 11px;
  font-weight: 600;
}

.workbench-section-heading h2 {
  margin: 7px 0 0;
  color: #302b28;
  font-size: 18px;
  font-weight: 650;
}

.workbench-section-heading__note {
  color: #948b86;
  font-size: 11px;
}

.capability-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.capability-card {
  min-height: 154px;
  padding: 20px 22px;
  border: 1px solid #eee9e5;
  border-radius: 6px;
  background: #fdfcfb;
}

.capability-card__index {
  color: #a77a74;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
}

.capability-card h3 {
  margin: 15px 0 7px;
  color: #38322f;
  font-size: 15px;
  font-weight: 650;
}

.capability-card p {
  margin: 0;
  color: #79716c;
  font-size: 12px;
  line-height: 1.8;
}

.workbench-boundary {
  display: flex;
  align-items: flex-start;
  gap: 11px;
  padding: 17px 20px;
  border-left: 3px solid #8f2428;
  background: #f1efed;
}

.workbench-boundary__mark {
  width: 6px;
  height: 6px;
  flex: none;
  margin-top: 7px;
  border-radius: 50%;
  background: #8f2428;
}

.workbench-boundary p {
  margin: 0;
  color: #625b57;
  font-size: 12px;
  line-height: 1.8;
}

@media (max-width: 760px) {
  .workbench-hero {
    min-height: 0;
    padding: 28px 24px;
  }

  .workbench-mark {
    display: none;
  }

  .workbench-hero h1 {
    font-size: 23px;
  }

  .workbench-capabilities {
    padding: 22px 18px;
  }

  .capability-grid {
    grid-template-columns: 1fr;
  }

  .capability-card {
    min-height: 0;
  }
}
</style>
