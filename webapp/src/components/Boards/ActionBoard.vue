<template>
  <NTabs
      class="action-board-tabs__container"
      default-value="endpoints"
      size="small"
      justify-content="center"
      type="line"
    >
    <NTabPane
        class="action-board-tabs__tab"
        name="endpoints"
        tab="Endpoints"
    >
      <Endpoints />
    </NTabPane>
    <NTabPane
        class="action-board-tabs__tab"
        name="templates"
        tab="Templates"
        display-directive="show:lazy"
    >
      <Template />
    </NTabPane>
    <NTabPane
        class="action-board-tabs__tab"
        name="log"
        tab="Log"
        display-directive="show"
    >
      <Log />
    </NTabPane>
    <NTabPane
        class="action-board-tabs__tab"
        name="keys"
        tab="API Keys"
    >
      <KeyForm :is-to-update="true"/>
    </NTabPane>
  </NTabs>
</template>

<script setup>
import {NTabPane, NTabs} from "naive-ui";
import KeyForm from "../Actions/KeyForm.vue";
import Template from "../Actions/Template.vue";
import Log from "../Actions/Log.vue";
import Endpoints from "../Actions/Endpoints.vue";
</script>

<style scoped>
.action-board-tabs__tab {
  margin-top: 18px;

}
</style>