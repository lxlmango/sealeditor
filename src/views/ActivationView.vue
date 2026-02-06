<template>
  <section class="screen active">
    <div class="config-card glass">
      <div class="section-title">输入激活码</div>
      <div class="item">
        <label>激活码</label>
        <input
          type="text"
          v-model.trim="activationCode"
          placeholder="请输入激活码"
          @keydown.enter="handleVerify"
        />
      </div>
      <div class="btn-group">
        <button class="btn-save" type="button" @click="enterExperience">体验模式</button>
        <button class="btn-draw" :class="{ loading: verifying }" :disabled="verifying" @click="handleVerify">
          继续
        </button>
      </div>
      <div class="assist">
        <span>激活码将自动绑定当前浏览器</span>
        <span :class="['status', activationStatus.state]">{{ activationStatus.text }}</span>
      </div>
      <div v-if="activationStatus.message" class="purchase-tip">
        <span>{{ activationStatus.message }}</span>
        <a v-if="purchaseUrl" :href="purchaseUrl" target="_blank" rel="noopener">去购买</a>
      </div>
    </div>

    <div class="benefit-grid">
      <div class="benefit-card">
        <div class="benefit-title">体验模式</div>
        <ul>
          <li>完整功能预览</li>
          <li>导出禁用或带水印</li>
          <li>适合快速体验</li>
        </ul>
      </div>
      <div class="benefit-card highlight">
        <div class="benefit-title">正式版</div>
        <ul>
          <li>高清透明 PNG 导出</li>
          <li>多尺寸/高分辨率</li>
          <li>人名章与公章全功能</li>
        </ul>
      </div>
    </div>
    <div class="example-strip">
      <div class="example-card">
        <div class="example-label">公司公章</div>
        <canvas ref="exampleOrgCanvas" class="example-canvas" width="160" height="160"></canvas>
      </div>
      <div class="example-card">
        <div class="example-label">人名章</div>
        <canvas ref="exampleNameCanvas" class="example-canvas" width="160" height="160"></canvas>
      </div>
      <div class="example-card">
        <div class="example-label">财务章</div>
        <canvas ref="exampleFinanceCanvas" class="example-canvas" width="160" height="160"></canvas>
      </div>
    </div>
    <div class="pricing-card">
      <div class="pricing-title">购买入口</div>
      <div class="pricing-grid">
        <div class="pricing-item">
          <strong>单次使用</strong>
          <span>适合临时需求</span>
        </div>
        <div class="pricing-item">
          <strong>月度套餐</strong>
          <span>适合多次使用</span>
        </div>
        <div class="pricing-item">
          <strong>永久授权</strong>
          <span>适合长期使用</span>
        </div>
      </div>
      <div class="pricing-actions">
        <a v-if="purchaseUrl" :href="purchaseUrl" target="_blank" rel="noopener" class="cta-purchase">
          <span class="cta-badge">推荐</span>
          去购买
        </a>
        <button class="btn-save cta-secondary" type="button" @click="enterExperience">先体验</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useActivation } from '../composables/useActivation.js'

const router = useRouter()
const route = useRoute()
const exampleOrgCanvas = ref(null)
const exampleNameCanvas = ref(null)
const exampleFinanceCanvas = ref(null)

const {
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
  setExperienceMode
} = useActivation()

async function handleVerify() {
  const ok = await verifyActivation()
  if (ok) {
    setExperienceMode(false)
    router.push('/instructions')
  }
}

function enterExperience() {
  setStatus('idle', '体验模式', '导出将带水印/限制分辨率')
  setExperienceMode(true)
  router.push('/instructions')
}

onMounted(async () => {
  drawExamples()

  if (route.query.force === '1') {
    setStatus('idle', '待验证', '')
    return
  }

  const stored = loadActivation()
  if (stored && !isExpired(stored.expiresAt)) {
    activationCode.value = stored.code
    const ok = await ensureActivationStillValid()
    if (ok) {
      router.replace('/instructions')
      return
    }
    clearActivation()
  } else if (stored) {
    clearActivation()
  }

  setStatus('idle', '待验证', '')
})

function drawExamples() {
  drawOrgSample(exampleOrgCanvas.value, {
    mainText: '某某有限公司',
    subText: '合同专用章'
  })
  drawOrgSample(exampleFinanceCanvas.value, {
    mainText: '某某有限公司',
    subText: '财务专用章'
  })
  drawNameSample(exampleNameCanvas.value, '张三')
}

function drawOrgSample(canvas, { mainText, subText }) {
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const size = canvas.width
  const cx = size / 2
  const cy = size / 2
  const color = '#E60012'
  ctx.clearRect(0, 0, size, size)
  ctx.strokeStyle = color
  ctx.shadowColor = 'rgba(120, 30, 20, 0.25)'
  ctx.shadowBlur = 2
  ctx.lineWidth = 3.2
  ctx.beginPath()
  ctx.arc(cx, cy, size * 0.41, 0, Math.PI * 2)
  ctx.stroke()
  ctx.fillStyle = color
  ctx.font = `bold ${Math.round(size * 0.115)}px 'SimSun', serif`
  ctx.textAlign = 'center'
  const angleRange = Math.PI * 1.1
  const start = -Math.PI / 2 - angleRange / 2
  const step = angleRange / (mainText.length - 1 || 1)
  for (let i = 0; i < mainText.length; i++) {
    const angle = start + i * step
    ctx.save()
    ctx.translate(cx + size * 0.285 * Math.cos(angle), cy + size * 0.285 * Math.sin(angle))
    ctx.rotate(angle + Math.PI / 2)
    ctx.fillText(mainText[i], 0, 0)
    ctx.restore()
  }
  if (subText) {
    ctx.font = `bold ${Math.round(size * 0.07)}px 'SimSun', serif`
    const subRange = Math.PI * 0.5
    const subStart = Math.PI / 2 - subRange / 2
    const subStep = subRange / (subText.length - 1 || 1)
    for (let i = 0; i < subText.length; i++) {
      const angle = subStart + i * subStep
      ctx.save()
      ctx.translate(cx + size * 0.345 * Math.cos(angle), cy + size * 0.345 * Math.sin(angle))
      ctx.rotate(angle - Math.PI / 2)
      ctx.fillText(subText[i], 0, 0)
      ctx.restore()
    }
  }

  // center star
  ctx.save()
  ctx.globalAlpha = 0.92
  ctx.translate(cx, cy)
  ctx.fillStyle = color
  drawStar(ctx, 0, 0, 5, size * 0.08, size * 0.035)
  ctx.restore()
  ctx.shadowBlur = 0
}

function drawNameSample(canvas, nameText) {
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const size = canvas.width
  const cx = size / 2
  const cy = size / 2
  const color = '#E60012'
  ctx.clearRect(0, 0, size, size)
  ctx.strokeStyle = color
  ctx.shadowColor = 'rgba(120, 30, 20, 0.25)'
  ctx.shadowBlur = 2
  ctx.lineWidth = 3.2
  ctx.strokeRect(8, 8, size - 16, size - 16)
  ctx.font = `bold ${Math.round(size * 0.28)}px 'SimSun', serif`
  ctx.fillStyle = color
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  const chars = nameText.split('')
  if (chars.length >= 2) {
    ctx.fillText(chars[0], cx, cy - size * 0.12)
    ctx.fillText(chars[1], cx, cy + size * 0.12)
  } else {
    ctx.fillText(nameText, cx, cy)
  }
  ctx.shadowBlur = 0
}

function drawStar(ctx, x, y, r, p, m) {
  ctx.beginPath()
  ctx.save()
  ctx.translate(x, y)
  ctx.rotate(Math.PI)
  ctx.moveTo(0, p)
  for (let i = 0; i < 2 * r; i++) {
    ctx.rotate(Math.PI / r)
    ctx.lineTo(0, i % 2 === 0 ? m : p)
  }
  ctx.fill()
  ctx.restore()
}
</script>
