<template>
  <div class="endpoints__endpoint-content_container">
    <NCard v-for="endpoint in endpoints" :key="endpoint" class="endpoints__endpoint-content_card" @click="copyEndpointToClipboard($event)">
      <div class="endpoints__endpoint-content_card-border">
        <NCode
          class="endpoints__endpoint-content_content"
          :code="endpoint"
          language="javascript"
       />
      </div>
    </NCard>
  </div>
</template>

<script setup>
import {NH5, NCard, NCode, useMessage} from "naive-ui";
import {reactive} from "vue";
import {hostname} from "../hostname"

const endpoints = reactive({
  perpetualTrade: `${hostname}/perpetual/trade/`,
  keys: `${hostname}/keys/`
})

const message = useMessage()
const copyEndpointToClipboard = async function (event) {
  const code = event.target.innerText;
  await navigator.clipboard.writeText(code)
  message.success('Endpoint copied to clipboard')
};


</script>

<style scoped>
.endpoints__endpoint-content_container {
  padding: 0px 10px;


}
.endpoints__endpoint-content_card {
  border: 1px solid rgba(256,256,256,0.4);
  padding: 10px;
  margin-bottom: 18px;


}

.endpoints__endpoint-content_card-border {
}

.endpoints__endpoint-content_content {
  text-align: start;
  margin: 40px 0px;

}
</style>