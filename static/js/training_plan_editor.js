// 训练计划编辑器
class TrainingPlanEditor {
  constructor() {
    this.currentDay = 0;
    this.planData = this.initializePlanData();
    this.favoriteExercises = this.loadFavoriteExercises();
    this.init();
  }
  
  init() {
    try {
      this.applyUserWeights();
      this.renderWeekCards();
      this.renderExerciseLibrary();
      this.setupEventListeners();
      this.updateCurrentDayDisplay();
      console.log('训练计划编辑器初始化完成');
    } catch (error) {
      console.error('训练计划编辑器初始化失败:', error);
    }
  }
  
  initializePlanData() {
    return {
      plan_name: "我的五分化计划",
      mode: "五分化",
      cycle_weeks: 8,
      week_schedule: this.getTemplateSchedule("五分化")
    };
  }

  // 获取训练模板
  getTemplateSchedule(mode) {
    const templates = {
      "五分化": [
        { weekday: "周一", body_parts: ["胸部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周二", body_parts: ["背部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周三", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周四", body_parts: ["肩部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周五", body_parts: ["腿部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周六", body_parts: ["手臂"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周日", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } }
      ],
      "三分化": [
        { weekday: "周一", body_parts: ["胸部", "肩部", "三头肌"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周二", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周三", body_parts: ["背部", "二头肌"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周四", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周五", body_parts: ["腿部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周六", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周日", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } }
      ],
      "推拉腿": [
        { weekday: "周一", body_parts: ["推"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周二", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周三", body_parts: ["拉"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周四", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周五", body_parts: ["腿"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周六", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周日", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } }
      ],
      "有氧运动": [
        { weekday: "周一", body_parts: ["有氧"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周二", body_parts: ["有氧"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周三", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周四", body_parts: ["有氧"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周五", body_parts: ["有氧"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周六", body_parts: ["有氧"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周日", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } }
      ],
      "功能性训练": [
        { weekday: "周一", body_parts: ["功能性"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周二", body_parts: ["功能性"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周三", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周四", body_parts: ["功能性"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周五", body_parts: ["功能性"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周六", body_parts: ["功能性"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周日", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } }
      ],
      "自定义": [
        { weekday: "周一", body_parts: ["自定义"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周二", body_parts: ["自定义"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周三", body_parts: ["自定义"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周四", body_parts: ["自定义"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周五", body_parts: ["自定义"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周六", body_parts: ["自定义"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周日", body_parts: ["自定义"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } }
      ]
    };
    
    return templates[mode] || templates["五分化"];
  }

  renderWeekCards() {
    const weekCardsContainer = document.getElementById('weekCards');
    if (!weekCardsContainer) return;
    
    weekCardsContainer.innerHTML = this.planData.week_schedule.map((day, index) => {
      const isActive = index === this.currentDay;
      const isRestDay = day.body_parts.includes('休息');
      const exerciseCount = Object.values(day.modules).reduce((sum, module) => sum + module.length, 0);
      
      return `
        <div class="week-card ${isActive ? 'active' : ''}" onclick="editor.selectDay(${index})">
          <div class="day-name">${day.weekday}</div>
          <div class="day-parts">${day.body_parts.join(' + ')}</div>
          ${exerciseCount > 0 ? `<div class="exercise-count">${exerciseCount}个动作</div>` : ''}
        </div>
      `;
    }).join('');
    
    this.updatePlanStats();
  }

  updatePlanStats() {
    let totalExercises = 0;
    let trainingDays = 0;
    let restDays = 0;
    let totalWeight = 0;
    
    this.planData.week_schedule.forEach(day => {
      const dayExercises = Object.values(day.modules).reduce((sum, module) => sum + module.length, 0);
      totalExercises += dayExercises;
      
      if (day.body_parts.includes('休息')) {
        restDays++;
      } else {
        trainingDays++;
      }
      
      // 计算总重量
      Object.values(day.modules).forEach(module => {
        module.forEach(exercise => {
          if (exercise.weight && !isNaN(exercise.weight)) {
            totalWeight += parseFloat(exercise.weight) * parseInt(exercise.sets || 1);
          }
        });
      });
    });
    
    const elements = {
      totalExercises: document.getElementById('totalExercises'),
      trainingDays: document.getElementById('trainingDays'),
      restDays: document.getElementById('restDays'),
      totalWeight: document.getElementById('totalWeight')
    };
    
    if (elements.totalExercises) elements.totalExercises.textContent = totalExercises;
    if (elements.trainingDays) elements.trainingDays.textContent = trainingDays;
    if (elements.restDays) elements.restDays.textContent = restDays;
    if (elements.totalWeight) elements.totalWeight.textContent = `${totalWeight.toFixed(1)}kg`;
  }

  getTotalExercises() {
    let total = 0;
    this.planData.week_schedule.forEach(day => {
      total += Object.values(day.modules).reduce((sum, module) => sum + module.length, 0);
    });
    return total;
  }

  // 加载喜欢的动作
  loadFavoriteExercises() {
    const saved = localStorage.getItem('favorite_exercises');
    return saved ? JSON.parse(saved) : [];
  }

  // 保存喜欢的动作
  saveFavoriteExercises() {
    localStorage.setItem('favorite_exercises', JSON.stringify(this.favoriteExercises));
  }

  // 保存用户的重量设置
  saveUserWeights() {
    const userWeights = {};
    this.planData.week_schedule.forEach(day => {
      Object.values(day.modules).forEach(module => {
        module.forEach(exercise => {
          if (exercise.weight !== undefined && exercise.weight !== '') {
            userWeights[exercise.name] = exercise.weight;
          }
        });
      });
    });
    localStorage.setItem('user_exercise_weights', JSON.stringify(userWeights));
  }

  // 加载用户的重量设置
  loadUserWeights() {
    const saved = localStorage.getItem('user_exercise_weights');
    return saved ? JSON.parse(saved) : {};
  }

  // 应用用户的重量设置
  applyUserWeights() {
    const userWeights = this.loadUserWeights();
    this.planData.week_schedule.forEach(day => {
      Object.values(day.modules).forEach(module => {
        module.forEach(exercise => {
          if (userWeights[exercise.name] && !exercise.weight) {
            exercise.weight = userWeights[exercise.name];
          }
        });
      });
    });
  }

  // 获取重量建议
  getWeightSuggestion(exerciseName, module) {
    const userWeights = this.loadUserWeights();
    const defaultWeight = this.getDefaultWeight(exerciseName, module);
    
    if (userWeights[exerciseName]) {
      return userWeights[exerciseName];
    }
    
    if (defaultWeight !== '') {
      return defaultWeight;
    }
    
    return '';
  }

  // 显示重量建议
  showWeightSuggestion(exerciseName, module) {
    const suggestion = this.getWeightSuggestion(exerciseName, module);
    if (suggestion) {
      this.showNotification(`建议重量: ${suggestion}kg`, 'info');
    }
  }

  // 添加喜欢的动作
  addFavoriteExercise(exerciseName) {
    const existingIndex = this.favoriteExercises.findIndex(fav => fav.name === exerciseName);
    if (existingIndex !== -1) {
      this.favoriteExercises[existingIndex].timestamp = Date.now();
    } else {
      this.favoriteExercises.push({
        name: exerciseName,
        timestamp: Date.now()
      });
    }
    this.saveFavoriteExercises();
    this.updateFavoriteButton(exerciseName, true);
    this.showNotification(`已添加"${exerciseName}"到喜欢列表`, 'success');
  }

  // 移除喜欢的动作
  removeFavoriteExercise(exerciseName) {
    this.favoriteExercises = this.favoriteExercises.filter(fav => fav.name !== exerciseName);
    this.saveFavoriteExercises();
    this.updateFavoriteButton(exerciseName, false);
    this.showNotification(`已从喜欢列表移除"${exerciseName}"`, 'info');
  }

  // 更新喜欢按钮状态
  updateFavoriteButton(exerciseName, isFavorite) {
    const buttons = document.querySelectorAll(`[data-exercise="${exerciseName}"] .favorite-btn`);
    buttons.forEach(btn => {
      if (isFavorite) {
        btn.classList.add('favorite-active');
        btn.title = '取消喜欢';
      } else {
        btn.classList.remove('favorite-active');
        btn.title = '添加到喜欢';
      }
    });
  }

  // 检查动作是否被喜欢
  isFavoriteExercise(exerciseName) {
    return this.favoriteExercises.some(fav => fav.name === exerciseName);
  }

  // 获取喜欢的动作
  getFavoriteExercises() {
    return this.favoriteExercises
      .sort((a, b) => b.timestamp - a.timestamp)
      .map(fav => fav.name);
  }

  // 渲染动作库
  renderExerciseLibrary() {
    const exerciseLibrary = document.querySelector('.exercise-library .body-parts');
    if (!exerciseLibrary) {
      console.warn('找不到动作库容器');
      return;
    }

    const favoriteExercises = this.getFavoriteExercises();
    
    // 定义所有动作数据
    const allExercises = {
      chest: [
        "杠铃卧推", "哑铃卧推", "上斜哑铃推", "下斜哑铃推", "器械推胸", 
        "绳索夹胸", "哑铃飞鸟", "上斜飞鸟", "下斜飞鸟", "窄距卧推"
      ],
      back: [
        "引体向上", "杠铃划船", "高位下拉", "坐姿绳索划船", "哑铃划船", 
        "T杠划船", "单臂哑铃划船", "直臂下拉", "反向飞鸟", "面拉"
      ],
      shoulders: [
        "坐姿哑铃推举", "杠铃推举", "哑铃侧平举", "哑铃前平举", "哑铃后束飞鸟", 
        "耸肩", "绳索侧平举", "阿诺德推举", "面拉", "反向飞鸟"
      ],
      legs: [
        "杠铃深蹲", "罗马尼亚硬拉", "腿举", "腿弯举", "小腿提踵", 
        "前蹲", "腿外展", "腿内收", "保加利亚分腿蹲", "哑铃深蹲"
      ],
      arms: [
        "杠铃弯举", "三头肌下拉", "哑铃弯举", "锤式弯举", "绳索下拉", 
        "窄距卧推", "牧师椅弯举", "仰卧臂屈伸", "绳索弯举", "钻石俯卧撑"
      ],
      core: [
        "平板支撑", "俄罗斯转体", "卷腹", "仰卧举腿", "侧平板", 
        "死虫式", "鸟狗式", "悬垂举腿", "仰卧两头起", "龙旗"
      ],
      cardio: [
        "跑步", "椭圆机", "动感单车", "划船机", "跳绳", "HIIT"
      ],
      functional: [
        "波比跳", "深蹲跳", "高抬腿", "开合跳", "俯卧撑", 
        "单腿深蹲", "梯子训练", "锥桶训练", "药球投掷", "壶铃摆动"
      ],
      stretch: [
        "动态拉伸", "静态拉伸", "胸部拉伸", "背部拉伸", "肩部拉伸", 
        "腿部拉伸", "手臂拉伸", "髋部拉伸", "瑜伽", "泡沫轴放松"
      ]
    };

    const partNames = {
      chest: "胸部",
      back: "背部", 
      shoulders: "肩部",
      legs: "腿部",
      arms: "手臂",
      core: "核心",
      cardio: "有氧",
      functional: "功能性",
      stretch: "拉伸"
    };

    let html = '';

    // 首先渲染喜欢的动作
    if (favoriteExercises.length > 0) {
      html += `
        <div class="part-category" data-part="favorites">
          <div class="part-header">
            <i class="fas fa-chevron-right"></i>
            <span><i class="fas fa-heart" style="color: #ff6b35;"></i> 我喜欢的</span>
          </div>
          <div class="part-exercises" style="display: none;">
      `;
      
      favoriteExercises.forEach(exerciseName => {
        html += `
          <div class="exercise-item" draggable="true" data-exercise="${exerciseName}">
            <span>${exerciseName}</span>
            <button class="favorite-btn favorite-active" onclick="editor.toggleFavorite('${exerciseName}')" title="取消喜欢">
              <i class="fas fa-heart"></i>
            </button>
          </div>
        `;
      });
      
      html += '</div></div>';
    }

    // 渲染各个部位的动作
    Object.keys(allExercises).forEach(part => {
      html += `
        <div class="part-category" data-part="${part}">
          <div class="part-header">
            <i class="fas fa-chevron-right"></i>
            <span>${partNames[part]}</span>
          </div>
          <div class="part-exercises" style="display: none;">
      `;
      
      allExercises[part].forEach(exerciseName => {
        const isFavorite = this.isFavoriteExercise(exerciseName);
        html += `
          <div class="exercise-item" draggable="true" data-exercise="${exerciseName}">
            <span>${exerciseName}</span>
            <button class="favorite-btn ${isFavorite ? 'favorite-active' : ''}" onclick="editor.toggleFavorite('${exerciseName}')" title="${isFavorite ? '取消喜欢' : '添加到喜欢'}">
              <i class="fas fa-heart"></i>
            </button>
          </div>
        `;
      });
      
      html += '</div></div>';
    });

    exerciseLibrary.innerHTML = html;
  }

  // 切换喜欢状态
  toggleFavorite(exerciseName) {
    if (this.isFavoriteExercise(exerciseName)) {
      this.removeFavoriteExercise(exerciseName);
    } else {
      this.addFavoriteExercise(exerciseName);
    }
  }

  selectDay(dayIndex) {
    this.currentDay = dayIndex;
    this.renderWeekCards();
    this.updateCurrentDayDisplay();
  }
  
  updateCurrentDayDisplay() {
    try {
      const currentDay = this.planData.week_schedule[this.currentDay];
      const titleElement = document.getElementById('currentDayTitle');
      if (titleElement) {
        titleElement.textContent = `${currentDay.weekday}：${currentDay.body_parts.join(' + ')}`;
      }
      this.renderAllModules();
    } catch (error) {
      console.error('更新当前天显示失败:', error);
    }
  }

  renderAllModules() {
    const currentDay = this.planData.week_schedule[this.currentDay];
    const modules = ['warmup', 'main', 'accessory', 'cooldown'];
    
    modules.forEach(module => {
      this.renderModule(module, currentDay.modules[module]);
    });
  }
  
  setupEventListeners() {
    // 模式选择
    document.querySelectorAll('.mode-option').forEach(option => {
      option.addEventListener('click', (e) => {
        document.querySelectorAll('.mode-option').forEach(o => o.classList.remove('active'));
        e.currentTarget.classList.add('active');
        this.changeMode(e.currentTarget.dataset.mode);
      });
    });
    
    // 部位分类切换
    document.addEventListener('click', (e) => {
      if (e.target.closest('.part-header')) {
        const header = e.target.closest('.part-header');
        const category = header.closest('.part-category');
        if (category && category.dataset.part) {
          this.togglePartCategory(category.dataset.part);
        }
      }
    });
    
    // 拖拽功能
    this.setupDragAndDrop();
    
    // 模块切换
    document.querySelectorAll('.module-toggle').forEach(toggle => {
      toggle.addEventListener('click', (e) => {
        const module = e.currentTarget.closest('.module-section');
        if (module) {
          this.toggleModule(module);
        }
      });
    });
  }
  
  changeMode(mode) {
    this.planData.mode = mode;
    this.planData.week_schedule = this.getTemplateSchedule(mode);
    this.renderWeekCards();
    this.updateCurrentDayDisplay();
    this.renderAllModules();
    this.showNotification(`已切换到${mode}模式`, 'success');
  }
  
  togglePartCategory(part) {
    const category = document.querySelector(`[data-part="${part}"]`);
    const exercises = category.querySelector('.part-exercises');
    const icon = category.querySelector('.part-header i');
    
    if (exercises.style.display === 'none') {
      exercises.style.display = 'block';
      icon.className = 'fas fa-chevron-down';
      category.classList.add('active');
    } else {
      exercises.style.display = 'none';
      icon.className = 'fas fa-chevron-right';
      category.classList.remove('active');
    }
  }
  
  setupDragAndDrop() {
    // 动作拖拽
    document.addEventListener('dragstart', (e) => {
      if (e.target.closest('.exercise-item')) {
        const item = e.target.closest('.exercise-item');
        e.dataTransfer.setData('text/plain', item.dataset.exercise);
        item.style.opacity = '0.5';
      }
    });
    
    document.addEventListener('dragend', (e) => {
      if (e.target.closest('.exercise-item')) {
        const item = e.target.closest('.exercise-item');
        item.style.opacity = '1';
      }
    });
    
    // 放置区域
    document.querySelectorAll('.exercise-drop-zone').forEach(zone => {
      zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
      });
      
      zone.addEventListener('dragleave', () => {
        zone.classList.remove('dragover');
      });
      
      zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        
        const exerciseName = e.dataTransfer.getData('text/plain');
        const module = zone.dataset.module;
        this.addExercise(exerciseName, module);
      });
    });
  }
  
  addExercise(exerciseName, module) {
    const currentDay = this.planData.week_schedule[this.currentDay];
    const exercise = {
      name: exerciseName,
      sets: this.getDefaultSets(exerciseName, module),
      weight: this.getDefaultWeight(exerciseName, module),
      reps: this.getDefaultReps(exerciseName, module),
      rest: this.getDefaultRest(exerciseName, module)
    };
    
    currentDay.modules[module].push(exercise);
    this.renderModule(module, currentDay.modules[module]);
    this.renderWeekCards();
    this.showNotification(`已添加"${exerciseName}"到${this.getModuleName(module)}模块`, 'success');
  }

  // 获取动作的默认参数
  getDefaultSets(exerciseName, module) {
    const warmupExercises = ['动态拉伸', '静态拉伸', '胸部拉伸', '背部拉伸', '肩部拉伸', '腿部拉伸', '手臂拉伸', '髋部拉伸'];
    const cardioExercises = ['跑步', '椭圆机', '动感单车', '划船机', '跳绳', 'HIIT'];
    const functionalExercises = ['波比跳', '深蹲跳', '高抬腿', '开合跳', '梯子训练', '锥桶训练'];
    
    if (warmupExercises.includes(exerciseName) || module === 'cooldown') {
      return '1';
    }
    if (cardioExercises.includes(exerciseName)) {
      return '1';
    }
    if (functionalExercises.includes(exerciseName)) {
      return '3';
    }
    if (module === 'warmup') {
      return '2';
    }
    if (module === 'main') {
      return '4';
    }
    return '3';
  }

  getDefaultReps(exerciseName, module) {
    const warmupExercises = ['动态拉伸', '静态拉伸', '胸部拉伸', '背部拉伸', '肩部拉伸', '腿部拉伸', '手臂拉伸', '髋部拉伸'];
    const cardioExercises = ['跑步', '椭圆机', '动感单车', '划船机', '跳绳', 'HIIT'];
    const coreExercises = ['平板支撑', '侧平板', '死虫式', '鸟狗式'];
    const functionalExercises = ['波比跳', '深蹲跳', '高抬腿', '开合跳', '梯子训练', '锥桶训练'];
    
    if (warmupExercises.includes(exerciseName) || module === 'cooldown') {
      return '10分钟';
    }
    if (cardioExercises.includes(exerciseName)) {
      return '20-30分钟';
    }
    if (coreExercises.includes(exerciseName)) {
      return '60秒';
    }
    if (functionalExercises.includes(exerciseName)) {
      if (exerciseName === '波比跳') return '10次';
      if (exerciseName === '深蹲跳') return '15次';
      if (exerciseName === '高抬腿' || exerciseName === '开合跳') return '30秒';
      if (exerciseName === '梯子训练') return '5分钟';
      if (exerciseName === '锥桶训练') return '8分钟';
      return '20次';
    }
    if (module === 'warmup') {
      return '15-20';
    }
    if (module === 'main') {
      return '8-10';
    }
    return '10-12';
  }

  getDefaultWeight(exerciseName, module) {
    const warmupExercises = ['动态拉伸', '静态拉伸', '胸部拉伸', '背部拉伸', '肩部拉伸', '腿部拉伸', '手臂拉伸', '髋部拉伸'];
    const cardioExercises = ['跑步', '椭圆机', '动感单车', '划船机', '跳绳', 'HIIT'];
    const coreExercises = ['平板支撑', '侧平板', '死虫式', '鸟狗式'];
    const functionalExercises = ['波比跳', '深蹲跳', '高抬腿', '开合跳', '梯子训练', '锥桶训练'];
    const bodyweightExercises = ['引体向上', '俯卧撑', '双杠臂屈伸', '深蹲', '单腿深蹲', '保加利亚分腿蹲'];
    
    // 不需要重量的动作
    if (warmupExercises.includes(exerciseName) || module === 'cooldown') {
      return '';
    }
    if (cardioExercises.includes(exerciseName)) {
      return '';
    }
    if (coreExercises.includes(exerciseName)) {
      return '';
    }
    if (functionalExercises.includes(exerciseName)) {
      return '';
    }
    if (bodyweightExercises.includes(exerciseName)) {
      return '';
    }
    
    // 根据动作类型设置默认重量
    const weightMap = {
      // 胸部动作
      '杠铃卧推': 60, '哑铃卧推': 20, '上斜哑铃推': 18, '下斜哑铃推': 18, '器械推胸': 50,
      '绳索夹胸': 15, '哑铃飞鸟': 12, '上斜飞鸟': 10, '下斜飞鸟': 10, '窄距卧推': 50,
      
      // 背部动作
      '杠铃划船': 40, '高位下拉': 45, '坐姿绳索划船': 35, '哑铃划船': 15, 'T杠划船': 30,
      '单臂哑铃划船': 12, '直臂下拉': 20, '反向飞鸟': 8, '面拉': 12,
      
      // 肩部动作
      '坐姿哑铃推举': 16, '杠铃推举': 40, '哑铃侧平举': 8, '哑铃前平举': 8, '哑铃后束飞鸟': 6,
      '耸肩': 20, '绳索侧平举': 8, '阿诺德推举': 14,
      
      // 腿部动作
      '杠铃深蹲': 80, '罗马尼亚硬拉': 70, '腿举': 100, '腿弯举': 30, '小腿提踵': 40,
      '前蹲': 60, '腿外展': 25, '腿内收': 25, '保加利亚分腿蹲': 12, '哑铃深蹲': 15,
      
      // 手臂动作
      '杠铃弯举': 20, '三头肌下拉': 25, '哑铃弯举': 8, '锤式弯举': 8, '绳索下拉': 20,
      '窄距卧推': 40, '牧师椅弯举': 15, '仰卧臂屈伸': 12, '绳索弯举': 15, '钻石俯卧撑': '',
      
      // 有氧和功能性动作
      'HIIT': '', '跳绳': '', '波比跳': '', '深蹲跳': '', '高抬腿': '', '开合跳': '',
      '梯子训练': '', '锥桶训练': '', '药球投掷': 8, '壶铃摆动': 16
    };
    
    return weightMap[exerciseName] || '';
  }

  getDefaultRest(exerciseName, module) {
    const warmupExercises = ['动态拉伸', '静态拉伸', '胸部拉伸', '背部拉伸', '肩部拉伸', '腿部拉伸', '手臂拉伸', '髋部拉伸'];
    const cardioExercises = ['跑步', '椭圆机', '动感单车', '划船机', '跳绳', 'HIIT'];
    const coreExercises = ['平板支撑', '侧平板', '死虫式', '鸟狗式'];
    const functionalExercises = ['波比跳', '深蹲跳', '高抬腿', '开合跳', '梯子训练', '锥桶训练'];
    
    if (warmupExercises.includes(exerciseName) || module === 'cooldown') {
      return '无';
    }
    if (cardioExercises.includes(exerciseName)) {
      return '无';
    }
    if (coreExercises.includes(exerciseName)) {
      return '60秒';
    }
    if (functionalExercises.includes(exerciseName)) {
      if (exerciseName === '波比跳' || exerciseName === '深蹲跳') return '90秒';
      if (exerciseName === '高抬腿' || exerciseName === '开合跳') return '60秒';
      if (exerciseName === '梯子训练' || exerciseName === '锥桶训练') return '90秒';
      return '60秒';
    }
    if (module === 'warmup') {
      return '30秒';
    }
    if (module === 'main') {
      return '3分钟';
    }
    return '90秒';
  }
  
  getModuleName(module) {
    const names = {
      warmup: '热身', main: '主训', accessory: '辅助', cooldown: '拉伸'
    };
    return names[module] || module;
  }
  
  renderModule(module, exercises) {
    const dropZone = document.querySelector(`[data-module="${module}"] .exercise-drop-zone`);
    if (!dropZone) {
      console.warn(`找不到模块 ${module} 的放置区域`);
      return;
    }
    
    if (exercises.length === 0) {
      dropZone.innerHTML = `
        <i class="fas fa-plus"></i>
        <p>拖拽${this.getModuleName(module)}动作至此</p>
      `;
    } else {
      dropZone.innerHTML = exercises.map((exercise, index) => 
        this.createExerciseCard(exercise, module, index)
      ).join('');
    }
  }

  createExerciseCard(exercise, module, index) {
    return `
      <div class="exercise-card" data-module="${module}" data-index="${index}">
        <div class="exercise-card-header">
          <div class="exercise-card-name">${exercise.name}</div>
          <div class="exercise-card-controls">
            <button class="card-control-btn" onclick="editor.removeExercise('${module}', ${index})" title="删除">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
        <div class="exercise-params">
          <div class="param-group">
            <div class="param-label">组数</div>
            <input type="text" class="param-input" value="${exercise.sets}" 
                   onchange="editor.updateExerciseParam('${module}', ${index}, 'sets', this.value)">
          </div>
          <div class="param-group">
            <div class="param-label">重量(kg)</div>
            <div style="display: flex; align-items: center; gap: 4px;">
              <input type="number" class="param-input" value="${exercise.weight || ''}" 
                     placeholder="0" min="0" step="0.5"
                     onchange="editor.updateExerciseParam('${module}', ${index}, 'weight', this.value)">
              <button class="weight-adjust-btn" onclick="editor.quickAdjustWeight('${module}', ${index}, -2.5)" title="减少2.5kg">
                <i class="fas fa-minus"></i>
              </button>
              <button class="weight-adjust-btn" onclick="editor.quickAdjustWeight('${module}', ${index}, 2.5)" title="增加2.5kg">
                <i class="fas fa-plus"></i>
              </button>
              <button class="weight-suggestion-btn" onclick="editor.showWeightSuggestion('${exercise.name}', '${module}')" title="重量建议">
                <i class="fas fa-lightbulb"></i>
              </button>
            </div>
          </div>
          <div class="param-group">
            <div class="param-label">次数</div>
            <input type="text" class="param-input" value="${exercise.reps}"
                   onchange="editor.updateExerciseParam('${module}', ${index}, 'reps', this.value)">
          </div>
          <div class="param-group">
            <div class="param-label">休息</div>
            <input type="text" class="param-input" value="${exercise.rest}"
                   onchange="editor.updateExerciseParam('${module}', ${index}, 'rest', this.value)">
          </div>
        </div>
      </div>
    `;
  }

  removeExercise(module, index) {
    const currentDay = this.planData.week_schedule[this.currentDay];
    const exercise = currentDay.modules[module][index];
    currentDay.modules[module].splice(index, 1);
    this.renderModule(module, currentDay.modules[module]);
    this.renderWeekCards();
    this.showNotification(`已删除"${exercise.name}"`, 'info');
  }

  updateExerciseParam(module, index, param, value) {
    const currentDay = this.planData.week_schedule[this.currentDay];
    currentDay.modules[module][index][param] = value;
    
    // 如果是更新重量，保存用户设置
    if (param === 'weight') {
      this.saveUserWeights();
    }
  }

  quickAdjustWeight(module, index, adjustment) {
    const currentDay = this.planData.week_schedule[this.currentDay];
    const exercise = currentDay.modules[module][index];
    const currentWeight = parseFloat(exercise.weight) || 0;
    const newWeight = Math.max(0, currentWeight + adjustment);
    exercise.weight = newWeight.toString();
    
    // 重新渲染模块以更新显示
    this.renderModule(module, currentDay.modules[module]);
    this.saveUserWeights();
    
    this.showNotification(`重量已调整为 ${newWeight}kg`, 'info');
  }
  
  toggleModule(module) {
    const content = module.querySelector('.module-content');
    const toggle = module.querySelector('.module-toggle');
    
    if (content.style.display === 'none') {
      content.style.display = 'block';
      toggle.classList.remove('collapsed');
    } else {
      content.style.display = 'none';
      toggle.classList.add('collapsed');
    }
  }

  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
      <span>${message}</span>
    `;
    
    Object.assign(notification.style, {
      position: 'fixed',
      top: '20px',
      right: '20px',
      padding: '12px 20px',
      borderRadius: '6px',
      color: 'white',
      fontSize: '14px',
      fontWeight: '500',
      zIndex: '10000',
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      minWidth: '250px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      backgroundColor: type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3',
      animation: 'slideInRight 0.3s ease-out'
    });
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.animation = 'slideOutRight 0.3s ease-in';
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 3000);
  }
}

// 全局函数
function goBack() {
  window.history.back();
}

function loadTemplate() {
  document.getElementById('templateModal').style.display = 'flex';
}

function closeTemplateModal() {
  document.getElementById('templateModal').style.display = 'none';
}

function selectTemplate(templateName) {
  if (editor) {
    editor.changeMode(templateName);
    closeTemplateModal();
    
    // 更新计划名称
    const planNameInput = document.getElementById('planName');
    if (planNameInput) {
      planNameInput.value = `我的${templateName}计划`;
    }
  }
}

function previewPlan() {
  if (editor) {
    const planName = document.getElementById('planName').value.trim();
    if (!planName) {
      alert('请输入计划名称！');
      return;
    }
    
    const previewWindow = window.open('', '_blank', 'width=900,height=700,scrollbars=yes');
    const previewHTML = editor.generatePreviewHTML();
    
    previewWindow.document.open();
    previewWindow.document.write(previewHTML);
    previewWindow.document.close();
  }
}

function savePlan() {
  if (editor) {
    const planName = document.getElementById('planName').value.trim();
    if (!planName) {
      alert('请输入计划名称！');
      return;
    }
    editor.planData.plan_name = planName;
    localStorage.setItem('training_plan', JSON.stringify(editor.planData));
    editor.showNotification('训练计划已保存！', 'success');
  }
}

function publishPlan() {
  if (editor) {
    const planName = document.getElementById('planName').value.trim();
    if (!planName) {
      alert('请先填写计划名称！');
      return;
    }
    
    // 检查是否有训练内容
    const hasContent = editor.planData.week_schedule.some(day => 
      Object.values(day.modules).some(module => module.length > 0)
    );
    
    if (!hasContent) {
      alert('请至少添加一些训练动作！');
      return;
    }
    
    editor.showNotification('发布功能开发中...', 'info');
  }
}

function copyDay() {
  if (editor) {
    editor.showNotification('复制功能开发中...', 'info');
  }
}

function clearDay() {
  if (editor) {
    if (confirm('确定要清空当前训练日的所有内容吗？')) {
      const currentDay = editor.planData.week_schedule[editor.currentDay];
      Object.keys(currentDay.modules).forEach(module => {
        currentDay.modules[module] = [];
      });
      Object.keys(currentDay.modules).forEach(module => {
        editor.renderModule(module, currentDay.modules[module]);
      });
      editor.renderWeekCards();
      editor.showNotification('已清空当前训练日', 'info');
    }
  }
}

function manageWeights() {
  if (editor) {
    editor.showNotification('重量管理功能开发中...', 'info');
  }
}

function addExerciseToModule(module) {
  if (editor) {
    editor.showNotification('请从动作库拖拽动作到对应模块', 'info');
  }
}

function searchExercises() {
  const searchTerm = document.getElementById('exerciseSearch').value.toLowerCase();
  const exerciseItems = document.querySelectorAll('.exercise-item');
  
  exerciseItems.forEach(item => {
    const exerciseName = item.querySelector('span').textContent.toLowerCase();
    if (exerciseName.includes(searchTerm)) {
      item.style.display = 'flex';
    } else {
      item.style.display = 'none';
    }
  });
}

// 初始化编辑器
let editor;
document.addEventListener('DOMContentLoaded', function() {
  try {
    console.log('开始初始化训练计划编辑器...');
    editor = new TrainingPlanEditor();
    console.log('训练计划编辑器初始化成功');
    
    // 页面加载完成后显示内容
    const container = document.querySelector('.plan-editor-container');
    if (container) {
      container.style.opacity = '1';
    }
  } catch (error) {
    console.error('训练计划编辑器初始化失败:', error);
    // 显示错误信息给用户
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: #f44336;
      color: white;
      padding: 20px;
      border-radius: 8px;
      z-index: 10000;
      text-align: center;
    `;
    errorDiv.innerHTML = `
      <h3>页面加载失败</h3>
      <p>训练计划编辑器初始化失败，请刷新页面重试</p>
      <button onclick="location.reload()" style="margin-top: 10px; padding: 8px 16px; border: none; border-radius: 4px; background: white; color: #f44336; cursor: pointer;">刷新页面</button>
    `;
    document.body.appendChild(errorDiv);
  }
});
