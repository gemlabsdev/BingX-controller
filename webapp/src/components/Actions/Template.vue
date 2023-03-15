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
      @mouseover.once="displayQuantityInfo"
  >
    <NCard class="template__code-content_card">
      <NCode
      class="template__code-content_content"
      :code="test"
      language="json"
   />
    </NCard>

  </div>
  <div class="endpoints__endpoint-content_container">
      <div class="endpoints__endpoint-content_content">
        <code class="endpoints__endpoint-content_route">
          POST ->
        </code>
        <code @click="copyEndpointToClipboard($event)">
          {{endpoints.perpetualTrade}}
        </code>
      </div>
  </div>
</template>

<script setup>
import {NSpace, NCard, NRadioGroup, NRadioButton, NCode, NIcon, useMessage} from "naive-ui";
import {computed, h, reactive, ref} from "vue";
import {hostname} from "../hostname.js";
import { CashOutline } from '@vicons/ionicons5'



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

const endpoints = reactive({
  perpetualTrade: `${hostname}/perpetual/trade/`,
  keys: `${hostname}/keys/`
})

const copyTemplateToClipboard = async function () {
  if (position.action == null || position.side == null || position.use == null) {
    message.error('Copy failed. Please select all fields')
    return
  }
  const code = document.querySelector('.template__code-content_content').innerText;
  await navigator.clipboard.writeText(code)
  message.success('Template copied to clipboard')
}

const copyEndpointToClipboard = async function (event) {
  const code = event.target.innerText;
  await navigator.clipboard.writeText(code)
  message.success('Endpoint copied to clipboard')
}

const displayQuantityInfo = function () {
  message.success('quantity: USDT', {
          icon: () => h(NIcon, null, { default: () => h(CashOutline) })
        })
};

</script>

<style scoped>
.template__code-content_container {

  margin-top: 29px;
  margin-bottom: 24px;
  padding: 0px 110px;

}
.template__code-content_card {
  border: 1px solid rgba(256,256,256,0.4);
}

.template__code-content_content {
  text-align: start;
}

.endpoints__endpoint-content_container {
  margin-bottom: 5px;
}

.endpoints__endpoint-content_content {
  color: rgba(256,256,256,0.4);
}
.endpoints__endpoint-content_route {
  color: #d19a66;
}

</style>