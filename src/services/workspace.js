import { apiRequest } from './api'
import { useAssetLibraryStore } from '../stores/assetLibrary'
import { useRuntimeStore } from '../stores/runtime'
import { useSimuBossStore } from '../stores/simuBoss'

let currentLoad = null
let loaded = false

export async function loadUserWorkspace({ force = false, token } = {}) {
  if (currentLoad && !force) return currentLoad
  if (loaded && !force) return Promise.resolve(null)

  currentLoad = apiRequest('/workspace', { token })
    .then(({ documents = {} }) => {
      useSimuBossStore().hydrate(documents.simuboss || {})
      useAssetLibraryStore().hydrate(documents.assets || {})
      useRuntimeStore().hydrate(documents.runtime || {})
      loaded = true
      return documents
    })
    .finally(() => {
      currentLoad = null
    })

  return currentLoad
}

export function isWorkspaceLoaded() {
  return loaded
}

export function clearWorkspaceLoadState() {
  currentLoad = null
  loaded = false
}
