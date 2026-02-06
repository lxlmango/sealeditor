<template>
  <div :class="['scene', isApp ? 'scene-app' : '']">
    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>
    <div class="bg-orb orb-3"></div>

    <div :class="['shell', isApp ? 'shell-app' : '']">
      <header v-if="!isApp" class="hero">
        <div class="badge">SEAL LAB</div>
        <h1 class="title">电子印章样式生成器</h1>
        <p class="subtitle">轻量、精细、可控。用于设计演示与授权场景的视觉印章样式。</p>
      </header>

      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isApp = computed(() => route.path.startsWith('/app'))
</script>
