import { apiRequest } from './api'
import { useAssetLibraryStore } from '../stores/assetLibrary'
import { useRuntimeStore } from '../stores/runtime'
import { useSimuBossStore } from '../stores/simuBoss'

let currentLoad = null

export async function loadUserWorkspace({ force = false, token } = {}) {
  if (currentLoad && !force) return currentLoad

  currentLoad = apiRequest('/workspace', { token })
    .then(({ documents = {} }) => {
      useSimuBossStore().hydrate(documents.simuboss || {})
      useAssetLibraryStore().hydrate(documents.assets || {})
      useRuntimeStore().hydrate(documents.runtime || {})
      return documents
    })
    .finally(() => {
      currentLoad = null
    })

  return currentLoad
}

export function clearWorkspaceLoadState() {
  currentLoad = null
}
