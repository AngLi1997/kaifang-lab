<script setup>
import { ref } from 'vue'
import { NButton, NForm, NFormItem, NInput, NTabPane, NTabs, NImage, NUpload } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import CommonPage from '@/components/page/CommonPage.vue'
import { useUserStore } from '@/store'
import api from '@/api'
import { is } from '~/src/utils'

const { t } = useI18n()
const userStore = useUserStore()
const isLoading = ref(false)

// 用户信息的表单
const infoFormRef = ref(null)
const infoForm = ref({
  avatar: userStore.avatar,
  username: userStore.name,
  nickname: userStore.userInfo?.nickname || '',
  email: userStore.email,
})
async function updateProfile() {
  isLoading.value = true
  infoFormRef.value?.validate(async (err) => {
    if (err) {
      isLoading.value = false
      return
    }
    const { nickname, email } = infoForm.value
    await api
      .updateProfile({ nickname, email })
      .then((res) => {
        userStore.setUserInfo({ nickname: res.data.nickname, email: res.data.email })
        isLoading.value = false
        $message.success(t('common.text.update_success'))
      })
      .catch(() => {
        isLoading.value = false
      })
  })
}
const isUploadingAvatar = ref(false)
async function uploadAvatar({ file, onFinish, onError }) {
  const formData = new FormData()
  formData.append('file', file.file)
  isUploadingAvatar.value = true
  try {
    const res = await api.uploadAvatar(formData)
    infoForm.value.avatar = res.data.avatar
    userStore.setUserInfo({ avatar: res.data.avatar })
    $message.success(t('views.profile.message_avatar_updated'))
    onFinish()
  } catch {
    onError()
  } finally {
    isUploadingAvatar.value = false
  }
}
const infoFormRules = {}

// 修改密码的表单
const passwordFormRef = ref(null)
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

async function updatePassword() {
  isLoading.value = true
  passwordFormRef.value?.validate(async (err) => {
    if (!err) {
      const data = { ...passwordForm.value, id: userStore.userId }
      await api
        .updatePassword(data)
        .then((res) => {
          $message.success(res.msg)
          passwordForm.value = {
            old_password: '',
            new_password: '',
            confirm_password: '',
          }
          isLoading.value = false
        })
        .catch(() => {
          isLoading.value = false
        })
    }
  })
}
const passwordFormRules = {
  old_password: [
    {
      required: true,
      message: t('views.profile.message_old_password_required'),
      trigger: ['input', 'blur', 'change'],
    },
  ],
  new_password: [
    {
      required: true,
      message: t('views.profile.message_new_password_required'),
      trigger: ['input', 'blur', 'change'],
    },
  ],
  confirm_password: [
    {
      required: true,
      message: t('views.profile.message_password_confirmation_required'),
      trigger: ['input', 'blur'],
    },
    {
      validator: validatePasswordStartWith,
      message: t('views.profile.message_password_confirmation_diff'),
      trigger: 'input',
    },
    {
      validator: validatePasswordSame,
      message: t('views.profile.message_password_confirmation_diff'),
      trigger: ['blur', 'password-input'],
    },
  ],
}
function validatePasswordStartWith(rule, value) {
  return (
    !!passwordForm.value.new_password &&
    passwordForm.value.new_password.startsWith(value) &&
    passwordForm.value.new_password.length >= value.length
  )
}
function validatePasswordSame(rule, value) {
  return value === passwordForm.value.new_password
}
</script>

<template>
  <CommonPage :show-header="false">
    <NTabs type="line" animated>
      <NTabPane name="website" :tab="$t('views.profile.label_modify_information')">
        <div class="m-30 flex items-center">
          <NForm
            ref="infoFormRef"
            label-placement="left"
            label-align="left"
            label-width="100"
            :model="infoForm"
            :rules="infoFormRules"
            class="w-400"
          >
            <NFormItem :label="$t('views.profile.label_avatar')" path="avatar">
              <div class="flex items-center gap-16">
                <NImage width="100" :src="infoForm.avatar"></NImage>
                <div>
                  <NUpload
                    accept="image/png,image/jpeg,image/webp,image/gif"
                    :show-file-list="false"
                    :custom-request="uploadAvatar"
                  >
                    <NButton :loading="isUploadingAvatar">
                      {{ $t('views.profile.button_upload_avatar') }}
                    </NButton>
                  </NUpload>
                  <div class="mt-8 text-12 opacity-60">
                    {{ $t('views.profile.text_avatar_hint') }}
                  </div>
                </div>
              </div>
            </NFormItem>
            <NFormItem :label="$t('views.profile.label_username')" path="username">
              <NInput :value="infoForm.username" type="text" disabled />
            </NFormItem>
            <NFormItem :label="$t('views.profile.label_nickname')" path="nickname">
              <NInput
                v-model:value="infoForm.nickname"
                type="text"
                :maxlength="30"
                :placeholder="$t('views.profile.placeholder_nickname')"
              />
            </NFormItem>
            <NFormItem :label="$t('views.profile.label_email')" path="email">
              <NInput
                v-model:value="infoForm.email"
                type="text"
                :placeholder="$t('views.profile.placeholder_email')"
              />
            </NFormItem>
            <NButton type="primary" :loading="isLoading" @click="updateProfile">
              {{ $t('common.buttons.update') }}
            </NButton>
          </NForm>
        </div>
      </NTabPane>
      <NTabPane name="contact" :tab="$t('views.profile.label_change_password')">
        <NForm
          ref="passwordFormRef"
          label-placement="left"
          label-align="left"
          :model="passwordForm"
          label-width="200"
          :rules="passwordFormRules"
          class="m-30 w-500"
        >
          <NFormItem :label="$t('views.profile.label_old_password')" path="old_password">
            <NInput
              v-model:value="passwordForm.old_password"
              type="password"
              show-password-on="mousedown"
              :placeholder="$t('views.profile.placeholder_old_password')"
            />
          </NFormItem>
          <NFormItem :label="$t('views.profile.label_new_password')" path="new_password">
            <NInput
              v-model:value="passwordForm.new_password"
              :disabled="!passwordForm.old_password"
              type="password"
              show-password-on="mousedown"
              :placeholder="$t('views.profile.placeholder_new_password')"
            />
          </NFormItem>
          <NFormItem :label="$t('views.profile.label_confirm_password')" path="confirm_password">
            <NInput
              v-model:value="passwordForm.confirm_password"
              :disabled="!passwordForm.new_password"
              type="password"
              show-password-on="mousedown"
              :placeholder="$t('views.profile.placeholder_confirm_password')"
            />
          </NFormItem>
          <NButton type="primary" :loading="isLoading" @click="updatePassword">
            {{ $t('common.buttons.update') }}
          </NButton>
        </NForm>
      </NTabPane>
    </NTabs>
  </CommonPage>
</template>
