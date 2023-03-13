<template>
  <NSpace vertical>
    <NRadioGroup>
      <NSpace>
        <NRadioGroup v-model:value="position.action" name="direction">
          <NRadioButton
            value="Open"
            label="Open"
            size="small"
          />
          <NRadioButton
            value="Close"
            label="Close"
            size="small"
          />
        </NRadioGroup>
        <NRadioGroup v-model:value="position.side" name="side">
          <NRadioButton
            value="Bid"
            label="Long"
            size="small"
          />
          <NRadioButton
            value="Ask"
            label="Short"
            size="small"
          />
        </NRadioGroup>
        <NRadioGroup v-model:value="position.use" name="use" >
          <NRadioButton
            :value="ticker"
            label="TradingView"
            :checked="true"
            size="small"
          />
          <NRadioButton
            value="BTCUSDT"
            label="JSON"
            size="small"
          />
        </NRadioGroup>
      </NSpace>
    </NRadioGroup>
  </NSpace>
  <div
      class="template__code-content_container"
      @click="copyTemplateToClipboard"
  >
    <NCard class="template__code-content_card">
      <NCode
      class="template__code-content_content"
      :code="test"
      language="json"
   />
    </NCard>

  </div>

</template>

<script setup>
import {NSpace, NCard, NRadioGroup, NRadioButton, NCode, useMessage} from "naive-ui";
import {computed, reactive, ref} from "vue";



const message = useMessage()
const ticker = '{{ticker}}'
const position = reactive({
                                  action:null,
                                  side: null,
                                  use: null
                                })

const test = computed(() => {
  return `
{
    "symbol": "${position.use}",
    "action": "${position.action}",
    "side": "${position.side}",
    "trade_type": "Market",
    "quantity": 10.0
 }`
})

const copyTemplateToClipboard = async function () {
  if (position.action == null || position.side == null || position.use == null) {
    message.error('Copy failed. Please select all fields')
    return
  }
  const code = document.querySelector('.template__code-content_content').innerText;
  await navigator.clipboard.writeText(code)
  message.success('Template copied to clipboard')
};

</script>

<style scoped>
.template__code-content_container {

  margin: 40px 0px;
  padding: 0px 110px;

}
.template__code-content_card {
  border: 1px solid rgba(256,256,256,0.4);
}

.template__code-content_content {
  text-align: start;
}
</style>