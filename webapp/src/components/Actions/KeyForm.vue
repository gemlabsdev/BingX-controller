<template>
<n-form ref="apiKeys">
  <NH3>
    {{ title }}
  </NH3>

  <n-form-item
      ref="publicKey"
      label="Public"
      path="public">
      <n-input
          @keydown.enter.prevent
          v-model:value="keys.public" />
  </n-form-item>
  <n-form-item
      ref="privateKey"
      label="Private"
      path="private">
      <n-input
        type="password"
        v-model:value="keys.private"
        @keydown.enter.prevent
      />
  </n-form-item>
    <div>
    <n-button
        round
        type="primary"
        :disabled="!keys.public || !keys.private"
        @click="handleValidation">
      Submit
    </n-button>
  </div>
</n-form>
</template>

<script setup>
import {NForm, NFormItem, NInput, NButton, useMessage, NH3} from "naive-ui";
import {ref} from "vue";

const props = defineProps(['isToUpdate'])
const emit = defineEmits(['submit'])

const title = ref(props.isToUpdate ? 'Update API keys' : 'Load API keys')
const apiKeys = ref(null)
const message = useMessage()
const keys = ref({
  public: null,
  private: null
})

const rules = {
  public: [
      {
        required: true,
        message: "Public key is required"
      }
    ],
  private: [
      {
        required: true,
        message: "Private key is required"
      }
    ]
}

async function postKeys() {
  const response = await fetch('http://127.0.0.1:8000/keys', {
    method: 'POST',
    body: JSON.stringify(keys.value)
  })
  const data = await response.json()

  return data.status

}

async function handleValidation(e) {
        e.preventDefault();
        apiKeys.value?.validate(
          async (errors) => {
            if (!errors) {
              try {
                const status = await postKeys();
                if (status !== 'SUCCESS') {
                  message.error("An error has occurred. Please try again")
                  return
                }
                if (props.isToUpdate) {
                  message.success('API keys were updated successfully');
                } else {
                  message.success('API keys were added successfully');
                }
                emit('submit');
              } catch (error) {
                message.error("An error has occurred")
              }
            } else {
              console.log(errors);
              message.error("An error has occurred")
            }
          }
        );
}


</script>

<style scoped>

</style>