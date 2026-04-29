<template>
  <div ref="chartRef" class="evm-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  data: { month: string; pv: number; ev: number; ac: number; cpi: number; spi: number }[]
}>()

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

function renderChart() {
  if (!chartRef.value || !props.data.length) return
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }
  chartInstance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['PV', 'EV', 'AC', 'CPI', 'SPI'] },
    xAxis: { type: 'category', data: props.data.map((d) => d.month) },
    yAxis: [
      { type: 'value', name: '金额' },
      { type: 'value', name: '指数', min: 0 },
    ],
    series: [
      { name: 'PV', type: 'line', data: props.data.map((d) => d.pv), smooth: true },
      { name: 'EV', type: 'line', data: props.data.map((d) => d.ev), smooth: true },
      { name: 'AC', type: 'line', data: props.data.map((d) => d.ac), smooth: true },
      { name: 'CPI', type: 'line', yAxisIndex: 1, data: props.data.map((d) => d.cpi), smooth: true, lineStyle: { type: 'dashed' } },
      { name: 'SPI', type: 'line', yAxisIndex: 1, data: props.data.map((d) => d.spi), smooth: true, lineStyle: { type: 'dashed' } },
    ],
  })
}

onMounted(() => {
  renderChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})

watch(() => props.data, renderChart, { deep: true })

function handleResize() {
  chartInstance?.resize()
}
</script>

<style scoped lang="scss">
.evm-chart {
  width: 100%;
  height: 400px;
}
</style>
