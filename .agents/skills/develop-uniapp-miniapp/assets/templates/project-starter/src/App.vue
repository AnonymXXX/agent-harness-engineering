<script setup lang="ts">
import { onLaunch, onShow } from '@dcloudio/uni-app'

// App.vue renders no template in mini-programs (or H5): the global modal lives in PageLayout.
onLaunch(() => {
  console.log('App Launch')
})

onShow(() => {
  console.log('App Show')
})
</script>

<style lang="scss">
@tailwind base;
@tailwind components;
@tailwind utilities;

page {
  background-color: #050505;
  color: #ffffff;
}

* {
  -webkit-tap-highlight-color: transparent;
}
</style>
