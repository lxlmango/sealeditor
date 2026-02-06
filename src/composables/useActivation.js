import { computed, reactive, ref } from 'vue'

const ACTIVATION_KEY = 'seal_activation'
const EXPERIENCE_KEY = 'seal_experience'

const activationStatus = reactive({
  state: 'idle',
  text: '待验证',
  message: ''
})

const activationCode = ref('')
const verifying = ref(false)

const purchaseUrl = computed(() => import.meta.env.VITE_PURCHASE_URL || '')
const verifyEndpoint = computed(() => import.meta.env.VITE_ACTIVATION_VERIFY_ENDPOINT || '/api/activation/verify')
const mockActivation = computed(() => import.meta.env.VITE_MOCK_ACTIVATION === 'true')

function setStatus(state, text, message = '') {
  activationStatus.state = state
  activationStatus.text = text
  activationStatus.message = message
}

function isExpired(expiresAt) {
  return !expiresAt || Date.now() > expiresAt
}

function loadActivation() {
  try {
    const raw = localStorage.getItem(ACTIVATION_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function saveActivation(payload) {
  localStorage.setItem(ACTIVATION_KEY, JSON.stringify(payload))
}

function clearActivation() {
  localStorage.removeItem(ACTIVATION_KEY)
}

async function verifyActivation() {
  if (!activationCode.value) {
    setStatus('idle', '请输入激活码')
    return false
  }

  verifying.value = true
  setStatus('warn', '验证中')

  try {
    let data = null
    if (mockActivation.value) {
      data = {
        valid: true,
        expiresAt: Date.now() + 24 * 60 * 60 * 1000,
        token: 'mock-token'
      }
    } else {
      const res = await fetch(verifyEndpoint.value, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: activationCode.value })
      })
      if (!res.ok) throw new Error('verify_failed')
      data = await res.json()
    }

    if (data && data.valid === true) {
      const expiresAt = data.expiresAt
        ? new Date(data.expiresAt).getTime()
        : Date.now() + 24 * 60 * 60 * 1000

      saveActivation({
        code: activationCode.value,
        expiresAt,
        token: data.token || ''
      })

      setStatus('ok', '已验证')
      return true
    }

    setStatus('idle', '激活码无效', '请到下单页面购买激活码')
    return false
  } catch {
    setStatus('idle', '验证失败', '请到下单页面购买激活码')
    return false
  } finally {
    verifying.value = false
  }
}

async function ensureActivationStillValid() {
  const stored = loadActivation()
  if (!stored || isExpired(stored.expiresAt)) {
    clearActivation()
    return false
  }

  if (mockActivation.value) return true

  try {
    const res = await fetch(verifyEndpoint.value, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: stored.code })
    })
    if (!res.ok) throw new Error('verify_failed')
    const data = await res.json()
    if (data && data.valid === true) {
      if (data.expiresAt) {
        saveActivation({
          code: stored.code,
          expiresAt: new Date(data.expiresAt).getTime(),
          token: data.token || stored.token || ''
        })
      }
      return true
    }
  } catch {
    // ignore
  }

  clearActivation()
  return false
}

export function useActivation() {
  return {
    activationCode,
    activationStatus,
    verifying,
    purchaseUrl,
    setStatus,
    verifyActivation,
    ensureActivationStillValid,
    loadActivation,
    clearActivation,
    isExpired,
    setExperienceMode,
    isExperienceMode,
    clearExperienceMode
  }
}

function setExperienceMode(enabled) {
  if (enabled) {
    localStorage.setItem(EXPERIENCE_KEY, '1')
  } else {
    localStorage.removeItem(EXPERIENCE_KEY)
  }
}

function isExperienceMode() {
  return localStorage.getItem(EXPERIENCE_KEY) === '1'
}

function clearExperienceMode() {
  localStorage.removeItem(EXPERIENCE_KEY)
}
