import uni from '@dcloudio/vite-plugin-uni'
import autoprefixer from 'autoprefixer'
import tailwindcss from 'tailwindcss'
import Components from 'unplugin-vue-components/vite'
import { defineConfig } from 'vite'
import { UnifiedViteWeappTailwindcssPlugin as uvwt } from 'weapp-tailwindcss/vite'

export default defineConfig(async () => {
  const { default: AutoImport } = await import('unplugin-auto-import/vite')

  return {
    plugins: [
      Components({
        dirs: ['src/components', 'src/pages*/**/components'],
        extensions: ['vue'],
        dts: 'src/components.d.ts',
        directoryAsNamespace: false,
      }),
      uni(),
      uvwt({
        rem2rpx: true,
      }),
      AutoImport({
        imports: ['vue', 'uni-app', 'pinia'],
        dts: './src/auto-imports.d.ts',
        dirs: ['src/hooks', 'src/stores', 'src/utils', 'src/api', 'src/constants'],
      }),
    ],
    css: {
      // vite-plugin-uni writes its own css.postcss, so Vite never reads postcss.config.js;
      // Tailwind has to be registered here or app.wxss keeps the raw @tailwind directives.
      postcss: {
        plugins: [tailwindcss(), autoprefixer()],
      },
      preprocessorOptions: {
        // uni-app pins Vite 5.2, which still calls the legacy Sass JS API.
        scss: { silenceDeprecations: ['legacy-js-api'] },
      },
    },
  }
})
