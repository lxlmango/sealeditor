<template>
  <section class="screen active">
    <div class="config-card glass">
      <div class="section-title">使用说明</div>
      <div class="item">
        <label>请务必认真阅读</label>
        <div class="notice">
          本工具用于生成电子文档的装饰性印章或模拟样图，<span class="danger">仅限合法合规用途</span>
          （如个人设计、PPT演示、已获得授权的电子签章/电子文件标识等）。<br /><br />
          <span class="danger">严禁伪造、变造公章或冒用他人/单位印章</span>。根据《刑法》第二百八十条，
          伪造国家机关公文、证件、印章或伪造公司、企业、事业单位、人民团体印章
          <span class="danger">可能构成犯罪并承担刑事责任</span>。情节较轻的，依据《治安管理处罚法》第五十二条也可能受到行政处罚。<br /><br />
          使用者应确保具备合法授权、真实需求与合法场景，
          <span class="danger">不得将本工具用于任何违法用途或具有欺诈、误导性质的行为</span>。
          由此产生的法律责任由使用者自行承担。
        </div>
      </div>
      <div class="btn-group">
        <button class="btn-save" @click="goToActivation">上一步</button>
        <button class="btn-draw" @click="goToApp">我已知悉</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useActivation } from '../composables/useActivation.js'

const router = useRouter()
const { ensureActivationStillValid, setStatus, isExperienceMode, clearActivation, clearExperienceMode } =
  useActivation()

function goToActivation() {
  clearActivation()
  clearExperienceMode()
  router.push({ path: '/', query: { force: '1' } })
}

async function goToApp() {
  if (!isExperienceMode()) {
    const ok = await ensureActivationStillValid()
    if (!ok) {
      setStatus('idle', '已过期', '请到下单页面购买激活码')
      router.replace('/')
      return
    }
  }
  router.push('/app')
}
</script>
