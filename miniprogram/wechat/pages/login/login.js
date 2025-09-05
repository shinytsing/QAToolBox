// pages/login/login.js
const app = getApp()

Page({
  data: {
    loginType: 'password', // password, phone, wechat
    formData: {
      username: '',
      password: '',
      phone: '',
      code: ''
    },
    countdown: 0,
    isLogging: false
  },

  onLoad() {
    console.log('登录页面加载')
    // 检查是否已登录
    if (app.globalData.token) {
      wx.switchTab({
        url: '/pages/index/index'
      })
    }
  },

  // 切换登录方式
  onSwitchLoginType(e) {
    const { type } = e.currentTarget.dataset
    this.setData({
      loginType: type,
      formData: {
        username: '',
        password: '',
        phone: '',
        code: ''
      }
    })
  },

  // 输入框变化
  onInputChange(e) {
    const { field } = e.currentTarget.dataset
    const { value } = e.detail
    this.setData({
      [`formData.${field}`]: value
    })
  },

  // 密码登录
  onPasswordLogin() {
    const { username, password } = this.data.formData
    if (!username || !password) {
      app.showToast('请填写用户名和密码')
      return
    }

    this.setData({ isLogging: true })
    app.showLoading('登录中...')

    wx.request({
      url: `${app.globalData.baseUrl}/auth/login/`,
      method: 'POST',
      data: {
        username: username,
        password: password
      },
      success: (res) => {
        app.hideLoading()
        this.setData({ isLogging: false })

        if (res.statusCode === 200) {
          const { token, user } = res.data.data
          app.login(token, user)
          app.showToast('登录成功', 'success')
          
          setTimeout(() => {
            wx.switchTab({
              url: '/pages/index/index'
            })
          }, 1500)
        } else {
          app.showToast(res.data.message || '登录失败')
        }
      },
      fail: (error) => {
        app.hideLoading()
        this.setData({ isLogging: false })
        app.showToast('网络错误，请重试')
        console.error('登录失败:', error)
      }
    })
  },

  // 手机号登录
  onPhoneLogin() {
    const { phone, code } = this.data.formData
    if (!phone || !code) {
      app.showToast('请填写手机号和验证码')
      return
    }

    this.setData({ isLogging: true })
    app.showLoading('登录中...')

    wx.request({
      url: `${app.globalData.baseUrl}/auth/phone-login/`,
      method: 'POST',
      data: {
        phone: phone,
        code: code
      },
      success: (res) => {
        app.hideLoading()
        this.setData({ isLogging: false })

        if (res.statusCode === 200) {
          const { token, user } = res.data.data
          app.login(token, user)
          app.showToast('登录成功', 'success')
          
          setTimeout(() => {
            wx.switchTab({
              url: '/pages/index/index'
            })
          }, 1500)
        } else {
          app.showToast(res.data.message || '登录失败')
        }
      },
      fail: (error) => {
        app.hideLoading()
        this.setData({ isLogging: false })
        app.showToast('网络错误，请重试')
        console.error('登录失败:', error)
      }
    })
  },

  // 微信登录
  onWechatLogin() {
    this.setData({ isLogging: true })
    app.showLoading('登录中...')

    wx.login({
      success: (res) => {
        if (res.code) {
          wx.request({
            url: `${app.globalData.baseUrl}/auth/wechat-login/`,
            method: 'POST',
            data: {
              code: res.code
            },
            success: (loginRes) => {
              app.hideLoading()
              this.setData({ isLogging: false })

              if (loginRes.statusCode === 200) {
                const { token, user } = loginRes.data.data
                app.login(token, user)
                app.showToast('登录成功', 'success')
                
                setTimeout(() => {
                  wx.switchTab({
                    url: '/pages/index/index'
                  })
                }, 1500)
              } else {
                app.showToast(loginRes.data.message || '登录失败')
              }
            },
            fail: (error) => {
              app.hideLoading()
              this.setData({ isLogging: false })
              app.showToast('网络错误，请重试')
              console.error('微信登录失败:', error)
            }
          })
        } else {
          app.hideLoading()
          this.setData({ isLogging: false })
          app.showToast('微信登录失败')
        }
      },
      fail: (error) => {
        app.hideLoading()
        this.setData({ isLogging: false })
        app.showToast('微信登录失败')
        console.error('微信登录失败:', error)
      }
    })
  },

  // 发送验证码
  onSendCode() {
    const { phone } = this.data.formData
    if (!phone) {
      app.showToast('请先输入手机号')
      return
    }

    if (!/^1[3-9]\d{9}$/.test(phone)) {
      app.showToast('请输入正确的手机号')
      return
    }

    wx.request({
      url: `${app.globalData.baseUrl}/auth/send-code/`,
      method: 'POST',
      data: {
        phone: phone
      },
      success: (res) => {
        if (res.statusCode === 200) {
          app.showToast('验证码已发送')
          this.startCountdown()
        } else {
          app.showToast(res.data.message || '发送失败')
        }
      },
      fail: (error) => {
        app.showToast('网络错误，请重试')
        console.error('发送验证码失败:', error)
      }
    })
  },

  // 开始倒计时
  startCountdown() {
    let countdown = 60
    this.setData({ countdown })

    const timer = setInterval(() => {
      countdown--
      this.setData({ countdown })

      if (countdown <= 0) {
        clearInterval(timer)
        this.setData({ countdown: 0 })
      }
    }, 1000)
  },

  // 注册
  onRegister() {
    wx.navigateTo({
      url: '/pages/register/register'
    })
  },

  // 忘记密码
  onForgotPassword() {
    wx.navigateTo({
      url: '/pages/forgot-password/forgot-password'
    })
  }
})
