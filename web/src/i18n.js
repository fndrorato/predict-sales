import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

import enTranslations from './translations/en.json'
import ptTranslations from './translations/pt.json'
import esTranslations from './translations/es.json'

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: enTranslations },
    pt: { translation: ptTranslations },
    es: { translation: esTranslations },
  },
  lng: 'pt',
  fallbackLng: 'pt',
  interpolation: {
    escapeValue: false,
  },
})

export default i18n