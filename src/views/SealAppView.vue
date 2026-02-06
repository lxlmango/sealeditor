<template>
  <section :class="['screen', 'active', 'seal-page', cleanPreview ? 'clean-mode' : '']">
    <div class="seal-layout">
      <aside class="template-panel">
        <div class="template-head">
          <div class="template-head-left">
            <div class="template-ico" aria-hidden="true"></div>
            <div class="template-title">印章模板</div>
          </div>
          <button class="template-collapse" type="button" aria-label="折叠">
            <span></span>
          </button>
        </div>
        <div class="template-scroll">
          <div class="template-list">
            <button
              v-for="item in templateLibrary"
              :key="item.id"
              type="button"
              :class="['template-item', selectedTemplate === item.id ? 'active' : '']"
              @click="selectTemplate(item)"
            >
              <div class="template-thumb">
                <img :src="item.img" :alt="item.label" loading="lazy" />
              </div>
              <div class="template-name">{{ item.label }}</div>
            </button>
          </div>
        </div>
      </aside>
      <div ref="previewCardRef" class="preview-card">
        <div class="card-title">实时预览</div>
        <div v-if="experienceMode" class="experience-pill">体验模式</div>
        <div class="preview-tools">
          <span>缩放</span>
          <input
            class="preview-zoom"
            type="range"
            min="0.6"
            max="1.6"
            step="0.05"
            v-model.number="previewZoom"
            @pointerdown="setActiveRange('previewZoom')"
            @pointerup="clearActiveRange('previewZoom')"
            @pointercancel="clearActiveRange('previewZoom')"
            @blur="clearActiveRange('previewZoom')"
            @focus="setActiveRange('previewZoom')"
          />
          <span class="preview-zoom-value">{{ Math.round(previewZoom * 100) }}%</span>
          <button class="preview-toggle" type="button" @click="cleanPreview = !cleanPreview">
            {{ cleanPreview ? '退出全屏' : '纯净预览' }}
          </button>
        </div>
        <canvas
          ref="canvasRef"
          width="400"
          height="400"
          :style="{ transform: `scale(${previewZoom})`, transformOrigin: 'center center' }"
          @pointerdown="onPointerDown"
          @pointermove="onPointerMove"
          @pointerup="onPointerUp"
          @pointerleave="onPointerLeave"
        ></canvas>
      </div>
      <div v-show="!cleanPreview" class="panel-shell">
        <div class="panel-wrap" :style="panelHeightStyle">
          <div ref="configCardRef" class="config-card">
        <div v-if="experienceMode" class="experience-banner">
          体验模式已开启：导出功能暂不可用。激活后可导出高清透明 PNG。
        </div>
        <div class="section-title">印章类型</div>
        <div class="grid-settings">
          <div class="item">
            <label>模式</label>
            <select v-model="seal.mode">
              <option value="org">单位公章</option>
              <option value="name">人名章</option>
            </select>
          </div>
          <div class="item" v-if="seal.mode === 'name'">
            <label>形状</label>
            <select v-model="nameSeal.shape">
              <option value="square">正方形</option>
              <option value="round">圆形</option>
              <option value="rect">长方形</option>
            </select>
          </div>
        </div>

        <div class="section-title">模板库</div>
        <div class="grid-settings">
          <div class="item full-width">
            <div class="notice">
              模板已移至左侧「印章模板」区域，点击即可一键套用。
            </div>
          </div>
        </div>

        <div class="section-title">内容</div>
        <div class="grid-settings" v-if="seal.mode === 'org'">
          <div class="item full-width">
            <label>主体文案</label>
            <input type="text" v-model="seal.mainText" />
          </div>
          <div class="item full-width">
            <label>下弧文案</label>
            <input type="text" v-model="seal.subText" />
          </div>
        </div>

        <div class="grid-settings" v-else>
          <div class="item full-width">
            <label>人名</label>
            <input type="text" v-model="nameSeal.nameText" maxlength="4" />
          </div>
          <div class="item full-width">
            <label>排版</label>
            <div class="preset-actions">
              <button class="btn-subtle" type="button" @click="applyQuickLayout('vertical')">竖排</button>
              <button class="btn-subtle" type="button" @click="applyQuickLayout('horizontal')">横排</button>
              <button class="btn-subtle" type="button" @click="applyQuickLayout('split')">拆字</button>
            </div>
            <div class="layout-inline">
              <label>自定义排版</label>
              <textarea v-model="nameSeal.customLayout" rows="2"></textarea>
            </div>
          </div>
          <div class="item">
            <label>字体</label>
            <select v-model="nameSeal.fontFamily">
              <option value="'SimSun', 'Songti SC', serif">宋体</option>
              <option value="'STSong', 'Songti SC', serif">华文宋体</option>
              <option value="'KaiTi', 'Kaiti SC', serif">楷体</option>
              <option value="'FangSong', 'FangSong', serif">仿宋</option>
              <option value="'Noto Serif SC', 'Source Han Serif SC', serif">思源宋体</option>
              <option value="'Noto Sans SC', 'Source Han Sans SC', sans-serif">思源黑体</option>
            </select>
          </div>
          <div class="item">
            <label>刻法</label>
            <select v-model="nameSeal.engraving">
              <option value="yang">阳刻</option>
              <option value="yin">阴刻</option>
            </select>
          </div>
          <div class="item full-width">
            <div class="font-preview" :style="{ fontFamily: nameSeal.fontFamily }">示例字样：张三</div>
          </div>
          <div class="item">
            <label>印章颜色</label>
            <input type="color" v-model="nameSeal.color" />
          </div>
        </div>

        <div class="section-title">文字与间距控制</div>
        <div class="grid-settings" v-if="seal.mode === 'org'">
          <div class="item align-top">
            <label>字体</label>
            <select v-model="seal.fontFamily">
              <option value="'SimSun', 'Songti SC', serif">宋体</option>
              <option value="'STSong', 'Songti SC', serif">华文宋体</option>
              <option value="'KaiTi', 'Kaiti SC', serif">楷体</option>
              <option value="'FangSong', 'FangSong', serif">仿宋</option>
              <option value="'Noto Serif SC', 'Source Han Serif SC', serif">思源宋体</option>
              <option value="'Noto Sans SC', 'Source Han Sans SC', sans-serif">思源黑体</option>
            </select>
            <div class="font-preview" :style="{ fontFamily: seal.fontFamily }">示例字样：电子印章</div>
          </div>
          <div class="item color-field align-top">
            <label>印章颜色</label>
            <input type="color" v-model="seal.sealColor" />
          </div>
          <div class="item">
            <label>上弧字号</label>
            <div
              :class="['range-wrap', activeRange === 'fontSize' ? 'is-active' : '']"
              :style="rangeStyle(seal.fontSize, 20, 45)"
            >
              <input
                class="range-input"
                type="range"
                min="20"
                max="45"
                v-model.number="seal.fontSize"
                @pointerdown="setActiveRange('fontSize')"
                @pointerup="clearActiveRange('fontSize')"
                @pointercancel="clearActiveRange('fontSize')"
                @blur="clearActiveRange('fontSize')"
                @focus="setActiveRange('fontSize')"
              />
              <span class="range-float" :style="{ left: rangePercent(seal.fontSize, 20, 45) + '%' }">
                {{ seal.fontSize }}
              </span>
            </div>
          </div>
          <div class="item">
            <label>下弧字号</label>
            <div
              :class="['range-wrap', activeRange === 'subFontSize' ? 'is-active' : '']"
              :style="rangeStyle(seal.subFontSize, 8, 25)"
            >
              <input
                class="range-input"
                type="range"
                min="8"
                max="25"
                v-model.number="seal.subFontSize"
                @pointerdown="setActiveRange('subFontSize')"
                @pointerup="clearActiveRange('subFontSize')"
                @pointercancel="clearActiveRange('subFontSize')"
                @blur="clearActiveRange('subFontSize')"
                @focus="setActiveRange('subFontSize')"
              />
              <span class="range-float" :style="{ left: rangePercent(seal.subFontSize, 8, 25) + '%' }">
                {{ seal.subFontSize }}
              </span>
            </div>
          </div>
          <div class="item">
            <label>下弧排版</label>
            <select v-model="seal.subLayout">
              <option value="arc">弧形</option>
              <option value="line">直排</option>
            </select>
          </div>
          <div class="item full-width">
            <button class="btn-subtle toggle-btn" type="button" @click="showAdvancedOrg = !showAdvancedOrg">
              {{ showAdvancedOrg ? '收起高级参数' : '展开高级参数' }}
            </button>
          </div>
          <div v-if="showAdvancedOrg" class="item">
            <label>上弧分布跨度</label>
            <div
              :class="['range-wrap', activeRange === 'mainSpan' ? 'is-active' : '']"
              :style="rangeStyle(seal.mainSpan, 1.0, 1.8)"
            >
              <input
                class="range-input"
                type="range"
                min="1.0"
                max="1.8"
                step="0.05"
                v-model.number="seal.mainSpan"
                @pointerdown="setActiveRange('mainSpan')"
                @pointerup="clearActiveRange('mainSpan')"
                @pointercancel="clearActiveRange('mainSpan')"
                @blur="clearActiveRange('mainSpan')"
                @focus="setActiveRange('mainSpan')"
              />
              <span class="range-float" :style="{ left: rangePercent(seal.mainSpan, 1.0, 1.8) + '%' }">
                {{ seal.mainSpan.toFixed(2) }}
              </span>
            </div>
          </div>
          <div v-if="showAdvancedOrg" class="item">
            <label>下弧分布跨度</label>
            <div
              :class="['range-wrap', activeRange === 'subSpan' ? 'is-active' : '']"
              :style="rangeStyle(seal.subSpan, 0.3, 1.2)"
            >
              <input
                class="range-input"
                type="range"
                min="0.3"
                max="1.2"
                step="0.05"
                v-model.number="seal.subSpan"
                @pointerdown="setActiveRange('subSpan')"
                @pointerup="clearActiveRange('subSpan')"
                @pointercancel="clearActiveRange('subSpan')"
                @blur="clearActiveRange('subSpan')"
                @focus="setActiveRange('subSpan')"
              />
              <span class="range-float" :style="{ left: rangePercent(seal.subSpan, 0.3, 1.2) + '%' }">
                {{ seal.subSpan.toFixed(2) }}
              </span>
            </div>
          </div>
          <div v-if="seal.subLayout === 'line'" class="item">
            <label>下弧字间距</label>
            <div
              :class="['range-wrap', activeRange === 'subLineSpacing' ? 'is-active' : '']"
              :style="rangeStyle(seal.subLineSpacing, 0, 24)"
            >
              <input
                class="range-input"
                type="range"
                min="0"
                max="24"
                v-model.number="seal.subLineSpacing"
                @pointerdown="setActiveRange('subLineSpacing')"
                @pointerup="clearActiveRange('subLineSpacing')"
                @pointercancel="clearActiveRange('subLineSpacing')"
                @blur="clearActiveRange('subLineSpacing')"
                @focus="setActiveRange('subLineSpacing')"
              />
              <span class="range-float" :style="{ left: rangePercent(seal.subLineSpacing, 0, 24) + '%' }">
                {{ seal.subLineSpacing }}
              </span>
            </div>
          </div>
        </div>
        <div class="grid-settings" v-else>
          <div class="item">
            <label>字号</label>
            <div
              :class="['range-wrap', activeRange === 'nameFontSize' ? 'is-active' : '']"
              :style="rangeStyle(nameSeal.fontSize, 26, 80)"
            >
              <input
                class="range-input"
                type="range"
                min="26"
                max="80"
                v-model.number="nameSeal.fontSize"
                @pointerdown="setActiveRange('nameFontSize')"
                @pointerup="clearActiveRange('nameFontSize')"
                @pointercancel="clearActiveRange('nameFontSize')"
                @blur="clearActiveRange('nameFontSize')"
                @focus="setActiveRange('nameFontSize')"
              />
              <span class="range-float" :style="{ left: rangePercent(nameSeal.fontSize, 26, 80) + '%' }">
                {{ nameSeal.fontSize }}
              </span>
            </div>
          </div>
          <div class="item">
            <label>字距</label>
            <div
              :class="['range-wrap', activeRange === 'nameSpacing' ? 'is-active' : '']"
              :style="rangeStyle(nameSeal.spacing, 2, 26)"
            >
              <input
                class="range-input"
                type="range"
                min="2"
                max="26"
                v-model.number="nameSeal.spacing"
                @pointerdown="setActiveRange('nameSpacing')"
                @pointerup="clearActiveRange('nameSpacing')"
                @pointercancel="clearActiveRange('nameSpacing')"
                @blur="clearActiveRange('nameSpacing')"
                @focus="setActiveRange('nameSpacing')"
              />
              <span class="range-float" :style="{ left: rangePercent(nameSeal.spacing, 2, 26) + '%' }">
                {{ nameSeal.spacing }}
              </span>
            </div>
          </div>
          <div class="item full-width">
            <button class="btn-subtle toggle-btn" type="button" @click="showAdvancedName = !showAdvancedName">
              {{ showAdvancedName ? '收起高级参数' : '展开高级参数' }}
            </button>
          </div>
          <template v-if="showAdvancedName">
            <div class="item">
              <label>边框粗细</label>
              <div
                :class="['range-wrap', activeRange === 'nameStroke' ? 'is-active' : '']"
                :style="rangeStyle(nameSeal.strokeWidth, 2, 10)"
              >
                <input
                  class="range-input"
                  type="range"
                  min="2"
                  max="10"
                  v-model.number="nameSeal.strokeWidth"
                  @pointerdown="setActiveRange('nameStroke')"
                  @pointerup="clearActiveRange('nameStroke')"
                  @pointercancel="clearActiveRange('nameStroke')"
                  @blur="clearActiveRange('nameStroke')"
                  @focus="setActiveRange('nameStroke')"
                />
                <span class="range-float" :style="{ left: rangePercent(nameSeal.strokeWidth, 2, 10) + '%' }">
                  {{ nameSeal.strokeWidth }}
                </span>
              </div>
            </div>
            <div class="item">
              <label>圆角</label>
              <div
                :class="['range-wrap', activeRange === 'nameCorner' ? 'is-active' : '']"
                :style="rangeStyle(nameSeal.cornerRadius, 0, 30)"
              >
                <input
                  class="range-input"
                  type="range"
                  min="0"
                  max="30"
                  v-model.number="nameSeal.cornerRadius"
                  @pointerdown="setActiveRange('nameCorner')"
                  @pointerup="clearActiveRange('nameCorner')"
                  @pointercancel="clearActiveRange('nameCorner')"
                  @blur="clearActiveRange('nameCorner')"
                  @focus="setActiveRange('nameCorner')"
                />
                <span class="range-float" :style="{ left: rangePercent(nameSeal.cornerRadius, 0, 30) + '%' }">
                  {{ nameSeal.cornerRadius }}
                </span>
              </div>
            </div>
          </template>
        </div>

        <div class="section-title">形态控制</div>
        <div class="grid-settings" v-if="seal.mode === 'org'">
          <div class="item">
            <label>图案选择</label>
            <select v-model="seal.centerLogo">
              <option value="star">五角星</option>
              <option value="text">中心字</option>
              <option value="none">无图案</option>
            </select>
          </div>
          <div class="item range-center">
            <label>图案大小</label>
            <div
              :class="['range-wrap', activeRange === 'centerSize' ? 'is-active' : '']"
              :style="rangeStyle(seal.centerSize, 10, 140)"
            >
              <input
                class="range-input"
                type="range"
                min="10"
                max="140"
                v-model.number="seal.centerSize"
                @pointerdown="setActiveRange('centerSize')"
                @pointerup="clearActiveRange('centerSize')"
                @pointercancel="clearActiveRange('centerSize')"
                @blur="clearActiveRange('centerSize')"
                @focus="setActiveRange('centerSize')"
              />
              <span class="range-float" :style="{ left: rangePercent(seal.centerSize, 10, 140) + '%' }">
                {{ seal.centerSize }}
              </span>
            </div>
          </div>
          <div class="item" v-if="showAdvancedOrg">
            <label>椭圆比例</label>
            <div
              :class="['range-wrap', activeRange === 'ellipseLevel' ? 'is-active' : '']"
              :style="rangeStyle(seal.ellipseLevel, 0, 100)"
            >
              <input
                class="range-input"
                type="range"
                min="0"
                max="100"
                v-model.number="seal.ellipseLevel"
                @pointerdown="setActiveRange('ellipseLevel')"
                @pointerup="clearActiveRange('ellipseLevel')"
                @pointercancel="clearActiveRange('ellipseLevel')"
                @blur="clearActiveRange('ellipseLevel')"
                @focus="setActiveRange('ellipseLevel')"
              />
              <span class="range-float" :style="{ left: rangePercent(seal.ellipseLevel, 0, 100) + '%' }">
                {{ seal.ellipseLevel }}
              </span>
            </div>
          </div>
          <div v-if="seal.centerLogo === 'text'" class="item full-width">
            <label>自定义中心文字内容</label>
            <input type="text" v-model="seal.centerText" maxlength="1" />
          </div>
        </div>
        <div class="grid-settings" v-else>
          <div class="item">
            <label>尺寸</label>
            <div
              :class="['range-wrap', activeRange === 'nameSize' ? 'is-active' : '']"
              :style="rangeStyle(nameSeal.size, 180, 320)"
            >
              <input
                class="range-input"
                type="range"
                min="180"
                max="320"
                v-model.number="nameSeal.size"
                @pointerdown="setActiveRange('nameSize')"
                @pointerup="clearActiveRange('nameSize')"
                @pointercancel="clearActiveRange('nameSize')"
                @blur="clearActiveRange('nameSize')"
                @focus="setActiveRange('nameSize')"
              />
              <span class="range-float" :style="{ left: rangePercent(nameSeal.size, 180, 320) + '%' }">
                {{ nameSeal.size }}
              </span>
            </div>
          </div>
          <div class="item" v-if="nameSeal.shape === 'rect'">
            <label>长宽比</label>
            <div
              :class="['range-wrap', activeRange === 'nameRatio' ? 'is-active' : '']"
              :style="rangeStyle(nameSeal.rectRatio, 1.1, 1.8)"
            >
              <input
                class="range-input"
                type="range"
                min="1.1"
                max="1.8"
                step="0.05"
                v-model.number="nameSeal.rectRatio"
                @pointerdown="setActiveRange('nameRatio')"
                @pointerup="clearActiveRange('nameRatio')"
                @pointercancel="clearActiveRange('nameRatio')"
                @blur="clearActiveRange('nameRatio')"
                @focus="setActiveRange('nameRatio')"
              />
              <span class="range-float" :style="{ left: rangePercent(nameSeal.rectRatio, 1.1, 1.8) + '%' }">
                {{ nameSeal.rectRatio.toFixed(2) }}
              </span>
            </div>
          </div>
          <div class="item">
            <label>椭圆比例</label>
            <div
              :class="['range-wrap', activeRange === 'nameEllipse' ? 'is-active' : '']"
              :style="rangeStyle(nameSeal.ellipseLevel, 0, 25)"
            >
              <input
                class="range-input"
                type="range"
                min="0"
                max="25"
                v-model.number="nameSeal.ellipseLevel"
                @pointerdown="setActiveRange('nameEllipse')"
                @pointerup="clearActiveRange('nameEllipse')"
                @pointercancel="clearActiveRange('nameEllipse')"
                @blur="clearActiveRange('nameEllipse')"
                @focus="setActiveRange('nameEllipse')"
              />
              <span class="range-float" :style="{ left: rangePercent(nameSeal.ellipseLevel, 0, 25) + '%' }">
                {{ nameSeal.ellipseLevel }}
              </span>
            </div>
          </div>
          <div class="item">
            <label>内框线</label>
            <select v-model="nameSeal.innerFrame">
              <option :value="true">开启</option>
              <option :value="false">关闭</option>
            </select>
          </div>
          <template v-if="showAdvancedName">
            <div class="item" v-if="nameSeal.innerFrame">
              <label>内框间距</label>
              <div
                :class="['range-wrap', activeRange === 'nameInset' ? 'is-active' : '']"
                :style="rangeStyle(nameSeal.innerFrameInset, 4, 24)"
              >
                <input
                  class="range-input"
                  type="range"
                  min="4"
                  max="24"
                  v-model.number="nameSeal.innerFrameInset"
                  @pointerdown="setActiveRange('nameInset')"
                  @pointerup="clearActiveRange('nameInset')"
                  @pointercancel="clearActiveRange('nameInset')"
                  @blur="clearActiveRange('nameInset')"
                  @focus="setActiveRange('nameInset')"
                />
                <span class="range-float" :style="{ left: rangePercent(nameSeal.innerFrameInset, 4, 24) + '%' }">
                  {{ nameSeal.innerFrameInset }}
                </span>
              </div>
            </div>
          </template>
        </div>

        <div class="section-title">导出尺寸</div>
        <div class="grid-settings">
          <div class="item full-width">
            <label>导出用途</label>
            <div class="preset-grid">
              <button
                v-for="option in exportUses"
                :key="option.value"
                type="button"
                :class="['preset-card', exportUse === option.value ? 'active' : '']"
                @click="selectExportUse(option.value)"
              >
                <strong>{{ option.label }}</strong>
                <span>{{ option.hint }}</span>
              </button>
            </div>
          </div>
          <div class="item">
            <label>常用尺寸</label>
            <select v-model="exportPreset">
              <option v-for="option in exportPresets" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          <div class="item" v-if="exportPreset !== 'custom'">
            <label>导出分辨率 (DPI)</label>
            <div
              :class="['range-wrap', activeRange === 'exportDpi' ? 'is-active' : '']"
              :style="rangeStyle(exportDpi, 150, 600)"
            >
              <input
                class="range-input"
                type="range"
                min="150"
                max="600"
                step="50"
                v-model.number="exportDpi"
                @pointerdown="setActiveRange('exportDpi')"
                @pointerup="clearActiveRange('exportDpi')"
                @pointercancel="clearActiveRange('exportDpi')"
                @blur="clearActiveRange('exportDpi')"
                @focus="setActiveRange('exportDpi')"
              />
              <span class="range-float" :style="{ left: rangePercent(exportDpi, 150, 600) + '%' }">
                {{ exportDpi }}
              </span>
            </div>
          </div>
          <div class="item" v-if="exportPreset === 'custom'">
            <label>自定义尺寸 (像素)</label>
            <input type="number" min="256" max="4096" step="1" v-model.number="exportCustomPx" />
          </div>
          <div class="item">
            <label>导出像素</label>
            <input type="text" :value="exportSizePxLabel" readonly />
          </div>
        </div>

        <div class="btn-group">
          <button class="btn-save" @click="resetPage">重置页面</button>
          <button class="btn-draw" :disabled="experienceMode" @click="handleExport">
            导出透明图片
          </button>
        </div>
        <div class="tip">
          {{ experienceMode ? '体验模式不可导出，请激活后使用' : saveTip }}
        </div>
        <div class="export-meta">
          PNG · 透明背景 · 自动命名
          <span v-if="exportUseLabel"> · 推荐：{{ exportUseLabel }}</span>
        </div>
      </div>
        </div>
      </div>
    </div>
    <div v-if="showUpgradeModal" class="modal-mask" @click.self="showUpgradeModal = false">
      <div class="modal-card">
        <h3>导出需要激活</h3>
        <p>体验模式仅可预览，激活后可导出高清透明 PNG。</p>
        <div class="modal-actions">
          <button class="btn-save" type="button" @click="showUpgradeModal = false">继续体验</button>
          <a v-if="purchaseUrl" :href="purchaseUrl" target="_blank" rel="noopener" class="btn-draw">
            去购买
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useActivation } from '../composables/useActivation.js'

const router = useRouter()
const { ensureActivationStillValid, setStatus, isExperienceMode, purchaseUrl } = useActivation()

const seal = reactive({
  mode: 'org',
  mainText: '电子签章研发测试中心',
  subText: '1101052026001',
  sealColor: '#ee0000',
  centerSize: 40,
  fontSize: 30,
  mainSpan: 1.35,
  subFontSize: 14,
  subSpan: 0.35,
  subLayout: 'arc',
  subLineSpacing: 6,
  centerLogo: 'star',
  ellipseLevel: 0,
  centerText: '章',
  fontFamily: "'SimSun', 'Songti SC', serif"
})

const nameSeal = reactive({
  nameText: '张三',
  layout: 'auto',
  direction: 'vertical',
  customLayout: '张\n三',
  shape: 'square',
  color: '#ee0000',
  engraving: 'yang',
  size: 240,
  rectRatio: 1.3,
  fontSize: 58,
  spacing: 8,
  strokeWidth: 6,
  cornerRadius: 10,
  ellipseLevel: 0,
  innerFrame: true,
  innerFrameInset: 10,
  fontFamily: "'SimSun', 'Songti SC', serif"
})

const saveTip = ref('导出完成后将自动下载图片')
const activeRange = ref(null)
const showAdvancedOrg = ref(false)
const showAdvancedName = ref(false)
const previewZoom = ref(1)
const cleanPreview = ref(false)
const showUpgradeModal = ref(false)
const canvasRef = ref(null)
const previewCardRef = ref(null)
const panelHeight = ref(null)
let ctx = null
const BASE_CANVAS_SIZE = 400

const exportPresets = [
  { value: '38', label: '38mm (常见人名章)' },
  { value: '40', label: '40mm (常见圆章)' },
  { value: '42', label: '42mm (单位常用)' },
  { value: '45', label: '45mm (单位常用)' },
  { value: 'custom', label: '自定义' }
]
const exportUses = [
  { value: 'ppt', label: 'PPT/方案', hint: '轻量清晰' },
  { value: 'contract', label: '合同/文档', hint: '标准清晰' },
  { value: 'print', label: '印刷/高清', hint: '高分辨率' },
  { value: 'xhs', label: '小红书分享', hint: '高清可传播' }
]
const exportPreset = ref('40')
const exportDpi = ref(300)
const exportCustomPx = ref(1200)
const exportUse = ref('ppt')

const exportUseLabel = computed(() => {
  const current = exportUses.find((use) => use.value === exportUse.value)
  return current ? current.label : ''
})

const orgPresets = [
  { value: 'default', label: '默认公章', hint: '适合常规文件', tag: '通用' },
  { value: 'company', label: '公司公章', hint: '公司文件/合同', tag: '公司' },
  { value: 'finance', label: '财务章', hint: '财务报销/票据', tag: '财务' },
  { value: 'contract', label: '合同章', hint: '合同/协议盖章', tag: '合同' }
]
const namePresets = [
  { value: 'two', label: '两字人名', hint: '个人签名/收据', tag: '人名' },
  { value: 'three', label: '三字人名', hint: '证书/签收', tag: '人名' },
  { value: 'four', label: '四字复姓', hint: '复姓姓名', tag: '复姓' }
]
const orgPreset = ref('default')
const namePreset = ref('two')
const selectedTemplate = ref('pic1')

const templateLibrary = [
  {
    id: 'pic1',
    label: '圆形印章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic1.png?x-oss-process=style/75X75',
    preset: 'default'
  },
  {
    id: 'pic2',
    label: '公章印章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic2.png?x-oss-process=style/75X75',
    preset: 'company'
  },
  {
    id: 'pic3',
    label: '分公司公章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic3.png?x-oss-process=style/75X75',
    preset: 'company'
  },
  {
    id: 'pic4',
    label: '合同专用章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic4.png?x-oss-process=style/75X75',
    preset: 'contract'
  },
  {
    id: 'pic5',
    label: '业务专用章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic5.png?x-oss-process=style/75X75',
    preset: 'finance'
  },
  {
    id: 'pic6',
    label: '椭圆印章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic6.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic7',
    label: '发票专用章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic7.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic8',
    label: '报关专用章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic8.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic9',
    label: '收费专用章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic9.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic34',
    label: '现金收讫',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic34.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic35',
    label: '财务章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic35.png?x-oss-process=style/75X75',
    preset: 'finance'
  },
  {
    id: 'pic10',
    label: '法人私章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic10.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic11',
    label: '菱形章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic11.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic12',
    label: '扁名章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic12.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic13',
    label: '执业章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic13.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic14',
    label: '造价章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic14.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic15',
    label: '认证章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic15.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic16',
    label: '骑缝章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic16.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic17',
    label: '指纹章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic17.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic18',
    label: '英文章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic18.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic19',
    label: '藏文章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic19.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic20',
    label: '香港章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic20.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic21',
    label: '维文章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic21.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic22',
    label: '条形章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic22.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic23',
    label: '质检小圆章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic23.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic24',
    label: '质检圆章2',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic24.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic36',
    label: '质检大圆章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic36.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic25',
    label: '质检方形章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic25.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic26',
    label: '作废小圆章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic26.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic27',
    label: '作废方形章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic27.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic28',
    label: '出货专用章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic28.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic29',
    label: '受控文件章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic29.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic30',
    label: '受控文件章2',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic30.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic31',
    label: '日期圆章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic31.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic32',
    label: '试制文件章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic32.png?x-oss-process=style/75X75'
  },
  {
    id: 'pic33',
    label: '检验椭圆章',
    img: 'https://ainitu.oss-cn-shanghai.aliyuncs.com/Aiimg/zy/img/pic33.png?x-oss-process=style/75X75'
  }
]

let dragOffsetX = 0
let dragOffsetY = 0
let isDragging = false
let lastPointerX = 0
let lastPointerY = 0

const OUTER_RADIUS = 185
const MAIN_TEXT_RADIUS = 132
const SUB_TEXT_RADIUS = 172
const DRAG_PADDING = 0
const SUB_TEXT_LINE_Y = OUTER_RADIUS - 35

function mmToPx(mm, dpi) {
  return Math.round((mm / 25.4) * dpi)
}

const exportSizePx = computed(() => {
  if (exportPreset.value === 'custom') {
    return Math.max(256, Math.min(4096, Number(exportCustomPx.value) || 1200))
  }
  const mm = Number(exportPreset.value)
  return mmToPx(mm, exportDpi.value)
})

const experienceMode = computed(() => isExperienceMode())
const effectiveExportSize = computed(() => {
  const size = exportSizePx.value
  if (!experienceMode.value) return size
  return Math.min(size, 800)
})

const exportSizePxLabel = computed(() => {
  return `${exportSizePx.value}px`
})

function resetPage() {
  window.location.reload()
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max)
}

function getCanvasScale(canvas) {
  const rect = canvas.getBoundingClientRect()
  return {
    scaleX: canvas.width / rect.width,
    scaleY: canvas.height / rect.height
  }
}

function onPointerDown(event) {
  if (!canvasRef.value) return
  if (experienceMode.value) {
    showUpgradeModal.value = true
    return
  }
  isDragging = true
  canvasRef.value.classList.add('dragging')
  const { scaleX, scaleY } = getCanvasScale(canvasRef.value)
  lastPointerX = (event.clientX - canvasRef.value.getBoundingClientRect().left) * scaleX
  lastPointerY = (event.clientY - canvasRef.value.getBoundingClientRect().top) * scaleY
  canvasRef.value.setPointerCapture(event.pointerId)
}

function syncCanvasSize() {
  if (!canvasRef.value) return
  const canvas = canvasRef.value
  if (cleanPreview.value) {
    const rect = canvas.getBoundingClientRect()
    const size = Math.floor(Math.min(rect.width, rect.height))
    if (size > 0 && (canvas.width !== size || canvas.height !== size)) {
      canvas.width = size
      canvas.height = size
      ctx = canvas.getContext('2d', { willReadFrequently: true })
      renderSeal()
    }
    return
  }
  if (canvas.width !== BASE_CANVAS_SIZE || canvas.height !== BASE_CANVAS_SIZE) {
    canvas.width = BASE_CANVAS_SIZE
    canvas.height = BASE_CANVAS_SIZE
    ctx = canvas.getContext('2d', { willReadFrequently: true })
    renderSeal()
  }
}

function onPointerMove(event) {
  if (!isDragging || !canvasRef.value) return
  const { scaleX, scaleY } = getCanvasScale(canvasRef.value)
  const x = (event.clientX - canvasRef.value.getBoundingClientRect().left) * scaleX
  const y = (event.clientY - canvasRef.value.getBoundingClientRect().top) * scaleY
  dragOffsetX += x - lastPointerX
  dragOffsetY += y - lastPointerY
  lastPointerX = x
  lastPointerY = y
  renderSeal()
}

function onPointerUp(event) {
  if (!canvasRef.value) return
  isDragging = false
  canvasRef.value.classList.remove('dragging')
  canvasRef.value.releasePointerCapture(event.pointerId)
}

function onPointerLeave() {
  if (!canvasRef.value) return
  isDragging = false
  canvasRef.value.classList.remove('dragging')
}

function drawStar(x, y, r, p, m) {
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

function renderSeal() {
  if (!ctx || !canvasRef.value) return

  saveTip.value = '导出完成后将自动下载图片'

  if (seal.mode === 'name') {
    renderNameSeal()
    return
  }

  const mainText = seal.mainText
  const subText = seal.subText
  const fontSize = seal.fontSize
  const subFontSize = seal.subFontSize
  const mainSpan = seal.mainSpan
  const subSpan = seal.subSpan
  const subLayout = seal.subLayout
  const subLineSpacing = seal.subLineSpacing
  const ellipseLevel = seal.ellipseLevel
  const color = seal.sealColor
  const logoType = seal.centerLogo
  const centerChar = seal.centerText || '章'
  const centerSize = seal.centerSize

  const scaleY = 1.0 - ellipseLevel / 200

  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  const cx = canvasRef.value.width / 2
  const cy = canvasRef.value.height / 2

  ctx.save()
  const maxOffsetX = Math.max(0, canvasRef.value.width / 2 - OUTER_RADIUS - DRAG_PADDING)
  const maxOffsetY = Math.max(0, canvasRef.value.height / 2 - OUTER_RADIUS - DRAG_PADDING)
  dragOffsetX = clamp(dragOffsetX, -maxOffsetX, maxOffsetX)
  dragOffsetY = clamp(dragOffsetY, -maxOffsetY, maxOffsetY)
  ctx.translate(cx + dragOffsetX, cy + dragOffsetY)
  ctx.scale(1, scaleY)

  ctx.strokeStyle = color
  ctx.lineWidth = 6
  ctx.beginPath()
  ctx.arc(0, 0, OUTER_RADIUS, 0, Math.PI * 2)
  ctx.stroke()

  ctx.save()
  ctx.scale(1, 1 / scaleY)
  ctx.fillStyle = color
  if (logoType === 'star') {
    drawStar(0, 0, 5, centerSize, centerSize * 0.4)
  } else if (logoType === 'text') {
    ctx.font = `bold ${centerSize * 1.5}px ${seal.fontFamily}`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(centerChar, 0, 0)
  }
  ctx.restore()

  ctx.font = `bold ${fontSize}px ${seal.fontFamily}`
  ctx.textAlign = 'center'
  const mainAngleRange = Math.PI * mainSpan
  const mainStartAngle = -Math.PI / 2 - mainAngleRange / 2
  const mainStep = mainAngleRange / (mainText.length - 1 || 1)

  for (let i = 0; i < mainText.length; i++) {
    const angle = mainStartAngle + i * mainStep
    ctx.save()
    ctx.translate(MAIN_TEXT_RADIUS * Math.cos(angle), MAIN_TEXT_RADIUS * Math.sin(angle))
    ctx.rotate(angle + Math.PI / 2)
    ctx.scale(1, 1 / scaleY)
    ctx.fillText(mainText[i], 0, 0)
    ctx.restore()
  }

  if (subText) {
    ctx.font = `bold ${subFontSize}px ${seal.fontFamily}`
    if (subLayout === 'line') {
      ctx.save()
      ctx.scale(1, 1 / scaleY)
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      drawTextWithSpacing(subText, 0, SUB_TEXT_LINE_Y, subLineSpacing)
      ctx.restore()
    } else {
      const subAngleRange = Math.PI * subSpan
      const subStart = Math.PI / 2 - subAngleRange / 2
      const subStep = subAngleRange / (subText.length - 1 || 1)

      for (let i = 0; i < subText.length; i++) {
        const angle = subStart + i * subStep
        ctx.save()
        ctx.translate(SUB_TEXT_RADIUS * Math.cos(angle), SUB_TEXT_RADIUS * Math.sin(angle))
        ctx.rotate(angle - Math.PI / 2)
        ctx.scale(1, 1 / scaleY)
        ctx.fillText(subText[i], 0, 0)
        ctx.restore()
      }
    }
  }

  ctx.restore()
}

function renderNameSeal() {
  if (!ctx || !canvasRef.value) return

  const size = nameSeal.size
  const ratio = nameSeal.shape === 'rect' ? nameSeal.rectRatio : 1
  const width = size * ratio
  const height = size
  const color = nameSeal.color
  const strokeWidth = nameSeal.strokeWidth
  const fontSize = nameSeal.fontSize
  const spacing = nameSeal.spacing
  const cornerRadius = nameSeal.cornerRadius
  const scaleY = 1.0 - nameSeal.ellipseLevel / 200
  const isYin = nameSeal.engraving === 'yin'

  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  const cx = canvasRef.value.width / 2
  const cy = canvasRef.value.height / 2

  ctx.save()
  ctx.translate(cx, cy)
  ctx.scale(1, scaleY)
  ctx.strokeStyle = color
  ctx.lineWidth = strokeWidth
  ctx.fillStyle = color

  if (nameSeal.shape === 'round') {
    ctx.beginPath()
    ctx.arc(0, 0, size / 2, 0, Math.PI * 2)
    if (isYin) ctx.fill()
    ctx.stroke()
  } else {
    drawRoundedRect(width, height, cornerRadius, isYin)
  }

  if (nameSeal.innerFrame) {
    const inset = Math.min(nameSeal.innerFrameInset, Math.min(width, height) / 2 - 4)
    const frameColor = isYin ? '#ffffff' : color
    ctx.save()
    ctx.strokeStyle = frameColor
    ctx.lineWidth = Math.max(1, strokeWidth - 2)
    if (nameSeal.shape === 'round') {
      ctx.beginPath()
      ctx.arc(0, 0, size / 2 - inset, 0, Math.PI * 2)
      ctx.stroke()
    } else {
      drawRoundedRect(width - inset * 2, height - inset * 2, Math.max(0, cornerRadius - inset), false)
    }
    ctx.restore()
  }

  ctx.save()
  ctx.scale(1, 1 / scaleY)
  ctx.fillStyle = isYin ? '#ffffff' : color
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.font = `bold ${fontSize}px ${nameSeal.fontFamily}`

  const layoutLines = getNameLines()
  const lines = layoutLines.length
  const lineHeight = fontSize + spacing
  const totalHeight = lineHeight * (lines - 1)

  if (lines <= 2) {
    layoutLines.forEach((line, idx) => {
      const y = -totalHeight / 2 + idx * lineHeight
      drawTextWithSpacing(line, 0, y, spacing)
    })
  } else {
    // 3~4字 -> 2x2
    const grid = layoutLines
    const gridSize = Math.min(2, Math.ceil(grid.length / 2))
    const cell = fontSize + spacing
    const startX = -cell / 2
    const startY = -cell / 2
    grid.forEach((char, idx) => {
      const col = idx % 2
      const row = Math.floor(idx / 2)
      const x = startX + col * cell
      const y = startY + row * cell
      ctx.fillText(char, x, y)
    })
  }

  ctx.restore()
  ctx.restore()
}

function drawRoundedRect(width, height, radius, fill) {
  const halfW = width / 2
  const halfH = height / 2
  const r = Math.min(radius, halfW - 2, halfH - 2)
  ctx.beginPath()
  ctx.moveTo(-halfW + r, -halfH)
  ctx.lineTo(halfW - r, -halfH)
  ctx.quadraticCurveTo(halfW, -halfH, halfW, -halfH + r)
  ctx.lineTo(halfW, halfH - r)
  ctx.quadraticCurveTo(halfW, halfH, halfW - r, halfH)
  ctx.lineTo(-halfW + r, halfH)
  ctx.quadraticCurveTo(-halfW, halfH, -halfW, halfH - r)
  ctx.lineTo(-halfW, -halfH + r)
  ctx.quadraticCurveTo(-halfW, -halfH, -halfW + r, -halfH)
  if (fill) ctx.fill()
  ctx.stroke()
}

function drawTextWithSpacing(text, x, y, spacing) {
  const chars = text.split('')
  if (chars.length <= 1) {
    ctx.fillText(text, x, y)
    return
  }

  const widths = chars.map((char) => ctx.measureText(char).width)
  const totalWidth =
    widths.reduce((sum, w) => sum + w, 0) + Math.max(0, chars.length - 1) * spacing
  let cursorX = x - totalWidth / 2

  chars.forEach((char, idx) => {
    const w = widths[idx]
    const centerX = cursorX + w / 2
    ctx.fillText(char, centerX, y)
    cursorX += w + spacing
  })
}

function setActiveRange(id) {
  activeRange.value = id
}

function clearActiveRange(id) {
  if (activeRange.value === id) {
    activeRange.value = null
  }
}

function rangePercent(value, min, max) {
  const v = Number(value)
  const pct = ((v - min) / (max - min)) * 100
  return Math.max(0, Math.min(100, pct))
}

function rangeStyle(value, min, max) {
  return {
    '--range-percent': `${rangePercent(value, min, max)}%`
  }
}

const panelHeightStyle = computed(() => {
  if (!panelHeight.value) return {}
  return { height: `${panelHeight.value}px` }
})

let resizeObserver = null
let stopCleanWatch = null

function syncPanelHeight() {
  if (typeof window === 'undefined') return
  const mq = window.matchMedia('(min-width: 900px)')
  if (!mq.matches || cleanPreview.value) {
    panelHeight.value = null
    return
  }
  if (!previewCardRef.value) return
  const rect = previewCardRef.value.getBoundingClientRect()
  panelHeight.value = Math.round(rect.height)
}

function applyOrgPreset() {
  switch (orgPreset.value) {
    case 'company':
      seal.mainText = '某某有限公司'
      seal.subText = '合同专用章'
      seal.centerLogo = 'star'
      seal.centerSize = 45
      seal.fontSize = 30
      seal.subFontSize = 12
      break
    case 'finance':
      seal.mainText = '某某有限公司'
      seal.subText = '财务专用章'
      seal.centerLogo = 'star'
      seal.centerSize = 42
      seal.fontSize = 30
      seal.subFontSize = 12
      break
    case 'contract':
      seal.mainText = '某某有限公司'
      seal.subText = '合同专用章'
      seal.centerLogo = 'star'
      seal.centerSize = 40
      seal.fontSize = 30
      seal.subFontSize = 12
      break
    default:
      seal.mainText = '电子签章研发测试中心'
      seal.subText = '1101052026001'
      seal.centerLogo = 'star'
      seal.centerSize = 40
      seal.fontSize = 30
      seal.subFontSize = 14
      break
  }
}

function selectOrgPreset(value) {
  orgPreset.value = value
  applyOrgPreset()
}

function applyNamePreset() {
  switch (namePreset.value) {
    case 'three':
      nameSeal.nameText = '王小明'
      nameSeal.layout = 'auto'
      nameSeal.direction = 'vertical'
      break
    case 'four':
      nameSeal.nameText = '欧阳娜娜'
      nameSeal.layout = 'auto'
      nameSeal.direction = 'vertical'
      break
    default:
      nameSeal.nameText = '张三'
      nameSeal.layout = 'auto'
      nameSeal.direction = 'vertical'
      break
  }
}

function selectNamePreset(value) {
  namePreset.value = value
  applyNamePreset()
}

function selectTemplate(item) {
  selectedTemplate.value = item.id
  if (item.preset && seal.mode === 'org') {
    selectOrgPreset(item.preset)
  }
}

function applyQuickLayout(type) {
  if (type === 'vertical') {
    nameSeal.layout = 'custom'
    nameSeal.direction = 'vertical'
    const raw = (nameSeal.nameText || '').replace(/\s+/g, '')
    if (raw) {
      nameSeal.customLayout = raw.split('').join('\n')
    }
    return
  }
  if (type === 'horizontal') {
    nameSeal.layout = 'custom'
    nameSeal.direction = 'horizontal'
    const raw = (nameSeal.nameText || '').replace(/\s+/g, '')
    if (raw) {
      nameSeal.customLayout = raw
    }
    return
  }
  const raw = (nameSeal.nameText || '').replace(/\s+/g, '')
  if (!raw) return
  nameSeal.layout = 'custom'
  nameSeal.customLayout = raw.split('').join('\n')
}

function selectExportUse(value) {
  exportUse.value = value
  if (value === 'ppt') {
    exportPreset.value = '40'
    exportDpi.value = 200
    return
  }
  if (value === 'contract') {
    exportPreset.value = '42'
    exportDpi.value = 300
    return
  }
  if (value === 'print') {
    exportPreset.value = '45'
    exportDpi.value = 600
    return
  }
  exportPreset.value = 'custom'
  exportCustomPx.value = 1200
}

function getNameLines() {
  const custom = (nameSeal.customLayout || '')
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
  if (custom.length > 0) {
    return custom
  }

  const raw = (nameSeal.nameText || '').replace(/\s+/g, '')
  if (nameSeal.direction === 'horizontal') {
    return [raw]
  }
  const chars = raw.split('')
  if (chars.length <= 2) return chars

  if (chars.length === 3 || chars.length === 4) {
    return chars
  }

  return [raw]
}

function handleExport() {
  if (!canvasRef.value) return
  const size = effectiveExportSize.value
  const out = document.createElement('canvas')
  out.width = size
  out.height = size
  const outCtx = out.getContext('2d')
  outCtx.clearRect(0, 0, out.width, out.height)
  outCtx.imageSmoothingEnabled = true
  outCtx.imageSmoothingQuality = 'high'
  outCtx.drawImage(canvasRef.value, 0, 0, size, size)

  const dataUrl = out.toDataURL('image/png')
  const stampLabel = seal.mode === 'org' ? '公章' : '人名章'
  const date = new Date()
  const dateTag = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(
    date.getDate()
  ).padStart(2, '0')}`
  const fileName = `${stampLabel}_${size}px_${dateTag}.png`
  const link = document.createElement('a')
  link.download = fileName
  link.href = dataUrl
  link.click()

  saveTip.value = `保存成功 · ${size}px${experienceMode.value ? '（体验水印）' : ''}`
}

async function ensureValidAccess() {
  if (!experienceMode.value) {
    const ok = await ensureActivationStillValid()
    if (!ok) {
      setStatus('idle', '已过期', '请到下单页面购买激活码')
      router.replace('/')
      return false
    }
  }
  return true
}

onMounted(async () => {
  syncPanelHeight()
  syncCanvasSize()
  window.addEventListener('resize', syncPanelHeight)
  window.addEventListener('resize', syncCanvasSize)
  if (previewCardRef.value && typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(syncPanelHeight)
    resizeObserver.observe(previewCardRef.value)
  }

  stopCleanWatch = watch(
    () => cleanPreview.value,
    () => {
      nextTick(syncPanelHeight)
      nextTick(syncCanvasSize)
    }
  )

  const ok = await ensureValidAccess()
  if (!ok) return

  if (canvasRef.value) {
    ctx = canvasRef.value.getContext('2d', { willReadFrequently: true })
  }

  await nextTick()
  renderSeal()
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', syncPanelHeight)
    window.removeEventListener('resize', syncCanvasSize)
  }
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  if (stopCleanWatch) {
    stopCleanWatch()
  }
})

watch(
  () => [
    seal.mode,
    seal.mainText,
    seal.subText,
    seal.sealColor,
    seal.centerSize,
    seal.fontSize,
    seal.mainSpan,
    seal.subFontSize,
    seal.subSpan,
    seal.subLayout,
    seal.subLineSpacing,
    seal.centerLogo,
    seal.ellipseLevel,
    seal.centerText,
    seal.fontFamily,
    nameSeal.nameText,
    nameSeal.layout,
    nameSeal.direction,
    nameSeal.customLayout,
    nameSeal.shape,
    nameSeal.color,
    nameSeal.engraving,
    nameSeal.size,
    nameSeal.rectRatio,
    nameSeal.fontSize,
    nameSeal.spacing,
    nameSeal.strokeWidth,
    nameSeal.cornerRadius,
    nameSeal.ellipseLevel,
    nameSeal.innerFrame,
    nameSeal.innerFrameInset,
    nameSeal.fontFamily
  ],
  () => {
    renderSeal()
  }
)
</script>
