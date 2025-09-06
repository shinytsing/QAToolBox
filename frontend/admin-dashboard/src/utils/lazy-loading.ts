import { defineAsyncComponent, type Component } from 'vue'

// 懒加载组件配置
const lazyComponents = {
  // 仪表盘组件
  Dashboard: () => import('@/views/Dashboard.vue'),
  StatsOverview: () => import('@/components/dashboard/StatsOverview.vue'),
  RecentActivity: () => import('@/components/dashboard/RecentActivity.vue'),
  
  // 用户管理组件
  UserList: () => import('@/components/users/UserList.vue'),
  UserForm: () => import('@/components/users/UserForm.vue'),
  UserProfile: () => import('@/components/users/UserProfile.vue'),
  
  // 健身管理组件
  FitnessOverview: () => import('@/components/fitness/FitnessOverview.vue'),
  WorkoutList: () => import('@/components/fitness/WorkoutList.vue'),
  WorkoutForm: () => import('@/components/fitness/WorkoutForm.vue'),
  AchievementList: () => import('@/components/fitness/AchievementList.vue'),
  
  // 生活工具组件
  LifeOverview: () => import('@/components/life/LifeOverview.vue'),
  DiaryList: () => import('@/components/life/DiaryList.vue'),
  DiaryForm: () => import('@/components/life/DiaryForm.vue'),
  CheckInList: () => import('@/components/life/CheckInList.vue'),
  
  // 极客工具组件
  GeekOverview: () => import('@/components/geek/GeekOverview.vue'),
  PDFList: () => import('@/components/geek/PDFList.vue'),
  CrawlerList: () => import('@/components/geek/CrawlerList.vue'),
  TestCaseList: () => import('@/components/geek/TestCaseList.vue'),
  
  // 社交娱乐组件
  SocialOverview: () => import('@/components/social/SocialOverview.vue'),
  ChatList: () => import('@/components/social/ChatList.vue'),
  HeartLinkList: () => import('@/components/social/HeartLinkList.vue'),
  TarotList: () => import('@/components/social/TarotList.vue'),
  
  // 分享管理组件
  ShareOverview: () => import('@/components/share/ShareOverview.vue'),
  ShareRecordList: () => import('@/components/share/ShareRecordList.vue'),
  ShareLinkList: () => import('@/components/share/ShareLinkList.vue'),
  
  // 设置组件
  SettingsOverview: () => import('@/components/settings/SettingsOverview.vue'),
  BasicSettings: () => import('@/components/settings/BasicSettings.vue'),
  FeatureSettings: () => import('@/components/settings/FeatureSettings.vue'),
  NotificationSettings: () => import('@/components/settings/NotificationSettings.vue'),
  
  // 图表组件
  LineChart: () => import('@/components/charts/LineChart.vue'),
  BarChart: () => import('@/components/charts/BarChart.vue'),
  PieChart: () => import('@/components/charts/PieChart.vue'),
  AreaChart: () => import('@/components/charts/AreaChart.vue'),
  
  // 表格组件
  DataTable: () => import('@/components/common/DataTable.vue'),
  Pagination: () => import('@/components/common/Pagination.vue'),
  SearchFilter: () => import('@/components/common/SearchFilter.vue'),
  
  // 表单组件
  FormBuilder: () => import('@/components/common/FormBuilder.vue'),
  FileUpload: () => import('@/components/common/FileUpload.vue'),
  ImageUpload: () => import('@/components/common/ImageUpload.vue'),
  
  // 模态框组件
  ConfirmDialog: () => import('@/components/common/ConfirmDialog.vue'),
  ImagePreview: () => import('@/components/common/ImagePreview.vue'),
  VideoPlayer: () => import('@/components/common/VideoPlayer.vue'),
}

// 创建懒加载组件
export function createLazyComponent(name: keyof typeof lazyComponents): Component {
  return defineAsyncComponent({
    loader: lazyComponents[name],
    loadingComponent: () => import('@/components/common/LoadingSpinner.vue'),
    errorComponent: () => import('@/components/common/ErrorBoundary.vue'),
    delay: 200,
    timeout: 10000,
    onError(error, retry, fail, attempts) {
      if (attempts <= 3) {
        retry()
      } else {
        fail()
      }
    }
  })
}

// 预加载组件
export function preloadComponent(name: keyof typeof lazyComponents): Promise<Component> {
  return lazyComponents[name]()
}

// 预加载多个组件
export function preloadComponents(names: (keyof typeof lazyComponents)[]): Promise<Component[]> {
  return Promise.all(names.map(name => lazyComponents[name]()))
}

// 路由懒加载
export const lazyRoutes = {
  dashboard: () => import('@/views/Dashboard.vue'),
  users: () => import('@/views/Users.vue'),
  fitness: () => import('@/views/Fitness.vue'),
  life: () => import('@/views/LifeTools.vue'),
  geek: () => import('@/views/GeekTools.vue'),
  social: () => import('@/views/Social.vue'),
  share: () => import('@/views/Share.vue'),
  settings: () => import('@/views/Settings.vue'),
}

// 动态导入工具函数
export function dynamicImport(path: string): Promise<any> {
  return import(/* webpackChunkName: "[request]" */ `@/${path}`)
}

// 条件加载组件
export function conditionalLoad(condition: boolean, componentName: keyof typeof lazyComponents): Component | null {
  if (condition) {
    return createLazyComponent(componentName)
  }
  return null
}

// 批量预加载
export function batchPreload(): Promise<void> {
  const criticalComponents = [
    'Dashboard',
    'UserList',
    'FitnessOverview',
    'LifeOverview',
    'GeekOverview',
    'SocialOverview'
  ] as const
  
  return preloadComponents(criticalComponents).then(() => {
    console.log('关键组件预加载完成')
  })
}

// 智能预加载
export function smartPreload(currentRoute: string): void {
  const preloadMap: Record<string, (keyof typeof lazyComponents)[]> = {
    '/dashboard': ['StatsOverview', 'RecentActivity'],
    '/users': ['UserList', 'UserForm'],
    '/fitness': ['FitnessOverview', 'WorkoutList'],
    '/life': ['LifeOverview', 'DiaryList'],
    '/geek': ['GeekOverview', 'PDFList'],
    '/social': ['SocialOverview', 'ChatList'],
    '/share': ['ShareOverview', 'ShareRecordList'],
    '/settings': ['SettingsOverview', 'BasicSettings']
  }
  
  const componentsToPreload = preloadMap[currentRoute] || []
  if (componentsToPreload.length > 0) {
    preloadComponents(componentsToPreload)
  }
}
