// 增强版训练计划编辑器
class EnhancedTrainingPlanEditor {
    constructor() {
        this.currentDay = 0;
        this.planData = this.initializePlanData();
        this.exerciseLibrary = {};
        this.templates = {};
        this.isDirty = false;
        
        this.init();
    }

    init() {
        this.loadExerciseLibrary();
        this.loadTemplates();
        this.renderDayTabs();
        this.renderCurrentDay();
        this.renderExerciseLibrary();
        this.bindEvents();
        
        // 自动保存
        setInterval(() => {
            if (this.isDirty) {
                this.autoSave();
            }
        }, 30000); // 30秒自动保存
    }

    initializePlanData() {
        return {
            name: '我的训练计划',
            description: '',
            plan_type: 'general_fitness',
            difficulty: 'beginner',
            duration_weeks: 8,
            training_days_per_week: 3,
            session_duration: 60,
            primary_goals: [],
            week_schedule: this.getDefaultSchedule()
        };
    }

    getDefaultSchedule() {
        return [
            { weekday: "周一", body_parts: ["胸部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
            { weekday: "周二", body_parts: ["背部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
            { weekday: "周三", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
            { weekday: "周四", body_parts: ["肩部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
            { weekday: "周五", body_parts: ["腿部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
            { weekday: "周六", body_parts: ["手臂"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
            { weekday: "周日", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } }
        ];
    }

    async loadExerciseLibrary() {
        try {
            // 扩展的动作库数据
            this.exerciseLibrary = {
                chest: [
                    {
                        name: "杠铃卧推",
                        english_name: "Barbell Bench Press",
                        difficulty: "intermediate",
                        type: "compound",
                        primary_muscles: ["胸大肌"],
                        secondary_muscles: ["前三角肌", "三头肌"],
                        equipment: ["杠铃", "卧推凳"],
                        description: "胸部训练的王牌动作，主要锻炼胸大肌",
                        instructions: "仰卧在卧推凳上，双手握杠铃，宽度略宽于肩膀，缓慢下降至胸部，然后用力推起",
                        form_cues: ["肩胛骨收紧", "核心保持稳定", "控制下降速度"],
                        sets_reps: "3-4组 x 6-8次",
                        rest_time: "2-3分钟"
                    },
                    {
                        name: "哑铃卧推",
                        english_name: "Dumbbell Bench Press",
                        difficulty: "beginner",
                        type: "compound",
                        primary_muscles: ["胸大肌"],
                        secondary_muscles: ["前三角肌", "三头肌"],
                        equipment: ["哑铃", "卧推凳"],
                        description: "使用哑铃进行的卧推动作，活动范围更大",
                        instructions: "仰卧持哑铃，双臂伸直，缓慢下降至胸部两侧，然后推起至起始位置",
                        form_cues: ["保持哑铃平衡", "肘部适度内收", "顶部不要碰撞"],
                        sets_reps: "3-4组 x 8-12次",
                        rest_time: "90秒-2分钟"
                    },
                    {
                        name: "上斜哑铃推举",
                        english_name: "Incline Dumbbell Press",
                        difficulty: "intermediate",
                        type: "compound",
                        primary_muscles: ["胸大肌上部"],
                        secondary_muscles: ["前三角肌", "三头肌"],
                        equipment: ["哑铃", "上斜凳"],
                        description: "针对胸大肌上部的专门训练动作",
                        instructions: "调整凳子角度30-45度，持哑铃推举",
                        form_cues: ["角度不要过陡", "保持核心稳定", "控制动作幅度"],
                        sets_reps: "3组 x 8-12次",
                        rest_time: "90秒"
                    },
                    {
                        name: "哑铃飞鸟",
                        english_name: "Dumbbell Flyes",
                        difficulty: "intermediate",
                        type: "isolation",
                        primary_muscles: ["胸大肌"],
                        secondary_muscles: [],
                        equipment: ["哑铃", "卧推凳"],
                        description: "孤立训练胸大肌的经典动作",
                        instructions: "仰卧持哑铃，手臂微屈，做飞鸟动作",
                        form_cues: ["保持肘部微屈", "感受胸部拉伸", "顶部挤压胸肌"],
                        sets_reps: "3组 x 10-15次",
                        rest_time: "60-90秒"
                    },
                    {
                        name: "双杠臂屈伸",
                        english_name: "Dips",
                        difficulty: "advanced",
                        type: "compound",
                        primary_muscles: ["胸大肌下部", "三头肌"],
                        secondary_muscles: ["前三角肌"],
                        equipment: ["双杠"],
                        description: "上肢力量训练的经典动作",
                        instructions: "双手撑杠，身体下降至肩部低于肘部，然后推起",
                        form_cues: ["身体前倾", "控制下降深度", "避免肩部受伤"],
                        sets_reps: "3组 x 8-15次",
                        rest_time: "2分钟"
                    },
                    {
                        name: "俯卧撑",
                        english_name: "Push-ups",
                        difficulty: "beginner",
                        type: "compound",
                        primary_muscles: ["胸大肌"],
                        secondary_muscles: ["前三角肌", "三头肌", "核心"],
                        equipment: ["自重"],
                        description: "经典的自重胸部训练动作",
                        instructions: "俯卧撑姿势，身体保持直线，上下推撑",
                        form_cues: ["保持身体直线", "核心收紧", "全程控制"],
                        sets_reps: "3组 x 10-20次",
                        rest_time: "60秒"
                    }
                ],
                back: [
                    {
                        name: "引体向上",
                        english_name: "Pull-ups",
                        difficulty: "intermediate",
                        type: "compound",
                        primary_muscles: ["背阔肌"],
                        secondary_muscles: ["二头肌", "后三角肌"],
                        equipment: ["引体向上杆"],
                        description: "上肢训练的经典动作，主要锻炼背阔肌",
                        instructions: "悬挂在单杠上，双手正握，身体向上拉至下巴超过杠子",
                        form_cues: ["肩胛骨下沉", "核心收紧", "避免摆动"],
                        sets_reps: "3-4组 x 6-12次",
                        rest_time: "2-3分钟"
                    },
                    {
                        name: "杠铃划船",
                        english_name: "Barbell Row",
                        difficulty: "intermediate",
                        type: "compound",
                        primary_muscles: ["背阔肌", "菱形肌"],
                        secondary_muscles: ["二头肌", "后三角肌"],
                        equipment: ["杠铃"],
                        description: "背部厚度训练的重要动作",
                        instructions: "俯身持杠铃，保持背部挺直，将杠铃拉至腹部",
                        form_cues: ["背部保持中立", "肩胛骨收缩", "肘部贴近身体"],
                        sets_reps: "3-4组 x 6-10次",
                        rest_time: "2-3分钟"
                    },
                    {
                        name: "高位下拉",
                        english_name: "Lat Pulldown",
                        difficulty: "beginner",
                        type: "compound",
                        primary_muscles: ["背阔肌"],
                        secondary_muscles: ["二头肌", "后三角肌"],
                        equipment: ["拉力器"],
                        description: "背部宽度训练的基础动作",
                        instructions: "坐姿，双手宽握横杆，向下拉至胸前",
                        form_cues: ["挺胸收肩", "肘部向后", "感受背部收缩"],
                        sets_reps: "3组 x 8-12次",
                        rest_time: "90秒"
                    },
                    {
                        name: "坐姿绳索划船",
                        english_name: "Seated Cable Row",
                        difficulty: "beginner",
                        type: "compound",
                        primary_muscles: ["背阔肌", "菱形肌"],
                        secondary_muscles: ["二头肌", "后三角肌"],
                        equipment: ["绳索"],
                        description: "安全有效的背部训练动作",
                        instructions: "坐姿，双手握把手，向后拉至腹部",
                        form_cues: ["保持躯干直立", "肩胛骨收缩", "控制还原"],
                        sets_reps: "3组 x 10-15次",
                        rest_time: "90秒"
                    },
                    {
                        name: "单臂哑铃划船",
                        english_name: "Single-Arm Dumbbell Row",
                        difficulty: "intermediate",
                        type: "compound",
                        primary_muscles: ["背阔肌"],
                        secondary_muscles: ["二头肌", "后三角肌"],
                        equipment: ["哑铃", "凳子"],
                        description: "单侧背部训练，纠正不平衡",
                        instructions: "单膝跪凳，单手持哑铃划船",
                        form_cues: ["保持背部平直", "肘部贴近身体", "感受背部收缩"],
                        sets_reps: "3组 x 8-12次/侧",
                        rest_time: "90秒"
                    },
                    {
                        name: "硬拉",
                        english_name: "Deadlift",
                        difficulty: "advanced",
                        type: "compound",
                        primary_muscles: ["下背部", "臀大肌", "股二头肌"],
                        secondary_muscles: ["背阔肌", "斜方肌"],
                        equipment: ["杠铃"],
                        description: "全身力量训练的王牌动作",
                        instructions: "双脚与肩同宽，俯身握杠，保持背部挺直，用腿部和臀部力量拉起杠铃",
                        form_cues: ["保持背部中立", "杠铃贴近身体", "髋部主导发力"],
                        sets_reps: "3-5组 x 3-6次",
                        rest_time: "3-5分钟"
                    }
                ],
                shoulders: [
                    {
                        name: "哑铃推举",
                        english_name: "Dumbbell Shoulder Press",
                        difficulty: "beginner",
                        type: "compound",
                        primary_muscles: ["前三角肌", "中三角肌"],
                        secondary_muscles: ["三头肌", "上胸"],
                        equipment: ["哑铃"],
                        description: "肩部训练的基础动作",
                        instructions: "坐姿或站姿，双手持哑铃，从肩部推举至头顶",
                        form_cues: ["核心收紧", "避免过度后仰", "控制下降"],
                        sets_reps: "3组 x 8-12次",
                        rest_time: "90秒"
                    },
                    {
                        name: "侧平举",
                        english_name: "Lateral Raises",
                        difficulty: "beginner",
                        type: "isolation",
                        primary_muscles: ["中三角肌"],
                        secondary_muscles: [],
                        equipment: ["哑铃"],
                        description: "专门训练三角肌中束的动作",
                        instructions: "双手持哑铃，手臂微屈，向两侧举起至肩高",
                        form_cues: ["保持肘部微屈", "控制动作速度", "顶部稍停"],
                        sets_reps: "3组 x 12-15次",
                        rest_time: "60秒"
                    },
                    {
                        name: "前平举",
                        english_name: "Front Raises",
                        difficulty: "beginner",
                        type: "isolation",
                        primary_muscles: ["前三角肌"],
                        secondary_muscles: [],
                        equipment: ["哑铃"],
                        description: "针对前三角肌的孤立训练",
                        instructions: "双手持哑铃，向前举起至肩高",
                        form_cues: ["避免借力摆动", "控制下降", "保持核心稳定"],
                        sets_reps: "3组 x 10-15次",
                        rest_time: "60秒"
                    },
                    {
                        name: "反向飞鸟",
                        english_name: "Reverse Flyes",
                        difficulty: "intermediate",
                        type: "isolation",
                        primary_muscles: ["后三角肌"],
                        secondary_muscles: ["菱形肌", "中斜方肌"],
                        equipment: ["哑铃"],
                        description: "训练后三角肌和改善体态",
                        instructions: "俯身或坐姿，双手持哑铃做反向飞鸟动作",
                        form_cues: ["保持肘部微屈", "挤压肩胛骨", "控制动作"],
                        sets_reps: "3组 x 12-15次",
                        rest_time: "60秒"
                    },
                    {
                        name: "阿诺德推举",
                        english_name: "Arnold Press",
                        difficulty: "intermediate",
                        type: "compound",
                        primary_muscles: ["全三角肌"],
                        secondary_muscles: ["三头肌"],
                        equipment: ["哑铃"],
                        description: "阿诺德·施瓦辛格创造的肩部训练动作",
                        instructions: "坐姿，双手持哑铃于胸前，旋转推举至头顶",
                        form_cues: ["动作流畅", "全程控制", "感受肩部各角度刺激"],
                        sets_reps: "3组 x 8-12次",
                        rest_time: "90秒"
                    },
                    {
                        name: "直立划船",
                        english_name: "Upright Rows",
                        difficulty: "intermediate",
                        type: "compound",
                        primary_muscles: ["中三角肌", "斜方肌"],
                        secondary_muscles: ["二头肌"],
                        equipment: ["杠铃", "哑铃"],
                        description: "肩部和斜方肌的复合训练",
                        instructions: "双手窄握杠铃，垂直向上拉至胸前",
                        form_cues: ["肘部引导", "不要拉得过高", "控制下降"],
                        sets_reps: "3组 x 10-12次",
                        rest_time: "90秒"
                    }
                ],
                legs: [
                    {
                        name: "杠铃深蹲",
                        english_name: "Barbell Squat",
                        difficulty: "intermediate",
                        type: "compound",
                        primary_muscles: ["股四头肌", "臀大肌"],
                        secondary_muscles: ["股二头肌", "核心"],
                        equipment: ["杠铃", "深蹲架"],
                        description: "腿部训练的王牌动作",
                        instructions: "杠铃置于肩上，双脚与肩同宽，下蹲至大腿平行地面",
                        form_cues: ["膝盖与脚尖同向", "保持胸挺背直", "重心在脚跟"],
                        sets_reps: "3-4组 x 6-10次",
                        rest_time: "2-3分钟"
                    },
                    {
                        name: "罗马尼亚硬拉",
                        english_name: "Romanian Deadlift",
                        difficulty: "intermediate",
                        type: "compound",
                        primary_muscles: ["股二头肌", "臀大肌"],
                        secondary_muscles: ["下背部"],
                        equipment: ["杠铃"],
                        description: "专门训练大腿后侧和臀部的动作",
                        instructions: "双手握杠，保持腿部微屈，髋部后推，杠铃沿腿部下降",
                        form_cues: ["髋部主导", "保持背部挺直", "感受大腿后侧拉伸"],
                        sets_reps: "3组 x 8-12次",
                        rest_time: "2分钟"
                    },
                    {
                        name: "腿举",
                        english_name: "Leg Press",
                        difficulty: "beginner",
                        type: "compound",
                        primary_muscles: ["股四头肌", "臀大肌"],
                        secondary_muscles: ["股二头肌"],
                        equipment: ["腿举机"],
                        description: "安全有效的腿部力量训练",
                        instructions: "坐在腿举机上，双脚推动重量板",
                        form_cues: ["保持膝盖稳定", "不要锁死膝关节", "控制下降"],
                        sets_reps: "3组 x 12-15次",
                        rest_time: "90秒"
                    },
                    {
                        name: "弓步蹲",
                        english_name: "Lunges",
                        difficulty: "beginner",
                        type: "compound",
                        primary_muscles: ["股四头肌", "臀大肌"],
                        secondary_muscles: ["股二头肌", "小腿"],
                        equipment: ["哑铃", "自重"],
                        description: "单腿训练，改善不平衡",
                        instructions: "一脚向前跨步，下蹲至前腿大腿平行地面",
                        form_cues: ["保持躯干直立", "后腿膝盖接近地面", "重心在前腿"],
                        sets_reps: "3组 x 10-12次/腿",
                        rest_time: "90秒"
                    },
                    {
                        name: "保加利亚分腿蹲",
                        english_name: "Bulgarian Split Squat",
                        difficulty: "intermediate",
                        type: "compound",
                        primary_muscles: ["股四头肌", "臀大肌"],
                        secondary_muscles: ["股二头肌"],
                        equipment: ["哑铃", "凳子"],
                        description: "高强度单腿训练动作",
                        instructions: "后脚置于凳上，前腿下蹲",
                        form_cues: ["重心在前腿", "保持平衡", "控制下降深度"],
                        sets_reps: "3组 x 8-12次/腿",
                        rest_time: "90秒"
                    },
                    {
                        name: "小腿提踵",
                        english_name: "Calf Raises",
                        difficulty: "beginner",
                        type: "isolation",
                        primary_muscles: ["小腿肌群"],
                        secondary_muscles: [],
                        equipment: ["哑铃", "器械"],
                        description: "专门训练小腿肌肉",
                        instructions: "脚尖着地，向上提起脚跟，感受小腿收缩",
                        form_cues: ["顶部停顿", "慢速下降", "全程控制"],
                        sets_reps: "3组 x 15-20次",
                        rest_time: "60秒"
                    }
                ],
                arms: [
                    {
                        name: "杠铃弯举",
                        english_name: "Barbell Curls",
                        difficulty: "beginner",
                        type: "isolation",
                        primary_muscles: ["二头肌"],
                        secondary_muscles: ["前臂"],
                        equipment: ["杠铃"],
                        description: "二头肌训练的经典动作",
                        instructions: "双手握杠铃，手臂弯举至胸前",
                        form_cues: ["肘部固定", "避免借力摆动", "控制下降"],
                        sets_reps: "3组 x 8-12次",
                        rest_time: "90秒"
                    },
                    {
                        name: "哑铃弯举",
                        english_name: "Dumbbell Curls",
                        difficulty: "beginner",
                        type: "isolation",
                        primary_muscles: ["二头肌"],
                        secondary_muscles: ["前臂"],
                        equipment: ["哑铃"],
                        description: "灵活的二头肌训练动作",
                        instructions: "双手持哑铃，交替或同时弯举",
                        form_cues: ["肘部贴近身体", "顶部挤压", "慢速下降"],
                        sets_reps: "3组 x 10-15次",
                        rest_time: "60秒"
                    },
                    {
                        name: "锤式弯举",
                        english_name: "Hammer Curls",
                        difficulty: "beginner",
                        type: "isolation",
                        primary_muscles: ["二头肌", "前臂"],
                        secondary_muscles: [],
                        equipment: ["哑铃"],
                        description: "训练二头肌外侧和前臂",
                        instructions: "双手持哑铃，保持中性握法弯举",
                        form_cues: ["保持手腕中立", "肘部稳定", "感受前臂参与"],
                        sets_reps: "3组 x 10-12次",
                        rest_time: "60秒"
                    },
                    {
                        name: "三头肌下拉",
                        english_name: "Tricep Pushdowns",
                        difficulty: "beginner",
                        type: "isolation",
                        primary_muscles: ["三头肌"],
                        secondary_muscles: [],
                        equipment: ["绳索"],
                        description: "三头肌训练的基础动作",
                        instructions: "站立，双手握绳索把手，向下推拉",
                        form_cues: ["肘部固定", "感受三头肌收缩", "控制还原"],
                        sets_reps: "3组 x 10-15次",
                        rest_time: "60秒"
                    },
                    {
                        name: "仰卧臂屈伸",
                        english_name: "Lying Tricep Extensions",
                        difficulty: "intermediate",
                        type: "isolation",
                        primary_muscles: ["三头肌"],
                        secondary_muscles: [],
                        equipment: ["杠铃", "哑铃"],
                        description: "三头肌深度刺激动作",
                        instructions: "仰卧持杠铃，肘部固定，进行臂屈伸",
                        form_cues: ["肘部不动", "控制重量", "感受三头肌拉伸"],
                        sets_reps: "3组 x 8-12次",
                        rest_time: "90秒"
                    },
                    {
                        name: "窄距俯卧撑",
                        english_name: "Close-Grip Push-ups",
                        difficulty: "intermediate",
                        type: "compound",
                        primary_muscles: ["三头肌", "胸肌"],
                        secondary_muscles: ["前三角肌"],
                        equipment: ["自重"],
                        description: "自重三头肌训练动作",
                        instructions: "双手窄距俯卧撑姿势，重点刺激三头肌",
                        form_cues: ["保持身体直线", "肘部贴近身体", "控制下降"],
                        sets_reps: "3组 x 8-15次",
                        rest_time: "90秒"
                    }
                ],
                core: [
                    {
                        name: "平板支撑",
                        english_name: "Plank",
                        difficulty: "beginner",
                        type: "isometric",
                        primary_muscles: ["腹直肌", "腹横肌"],
                        secondary_muscles: ["下背部", "肩部"],
                        equipment: ["自重"],
                        description: "核心稳定性训练的基础动作",
                        instructions: "俯卧撑姿势，用前臂支撑，保持身体直线",
                        form_cues: ["身体保持直线", "核心收紧", "正常呼吸"],
                        sets_reps: "3组 x 30-60秒",
                        rest_time: "60秒"
                    },
                    {
                        name: "卷腹",
                        english_name: "Crunches",
                        difficulty: "beginner",
                        type: "isolation",
                        primary_muscles: ["腹直肌上部"],
                        secondary_muscles: [],
                        equipment: ["自重"],
                        description: "腹肌训练的经典动作",
                        instructions: "仰卧，膝盖弯曲，上身向上卷起",
                        form_cues: ["下背部贴地", "用腹肌发力", "顶部挤压"],
                        sets_reps: "3组 x 15-25次",
                        rest_time: "60秒"
                    },
                    {
                        name: "俄罗斯转体",
                        english_name: "Russian Twists",
                        difficulty: "intermediate",
                        type: "compound",
                        primary_muscles: ["腹斜肌"],
                        secondary_muscles: ["腹直肌"],
                        equipment: ["自重", "药球"],
                        description: "训练腹斜肌和旋转力量",
                        instructions: "坐姿，身体后倾，双手左右转动",
                        form_cues: ["保持平衡", "核心收紧", "控制转动"],
                        sets_reps: "3组 x 20-30次",
                        rest_time: "60秒"
                    },
                    {
                        name: "仰卧举腿",
                        english_name: "Leg Raises",
                        difficulty: "intermediate",
                        type: "isolation",
                        primary_muscles: ["腹直肌下部"],
                        secondary_muscles: ["髋屈肌"],
                        equipment: ["自重"],
                        description: "针对下腹部的训练动作",
                        instructions: "仰卧，双腿伸直向上举起",
                        form_cues: ["下背部贴地", "腿部保持直立", "控制下降"],
                        sets_reps: "3组 x 10-15次",
                        rest_time: "60秒"
                    },
                    {
                        name: "死虫式",
                        english_name: "Dead Bug",
                        difficulty: "intermediate",
                        type: "compound",
                        primary_muscles: ["腹横肌", "腹直肌"],
                        secondary_muscles: ["下背部"],
                        equipment: ["自重"],
                        description: "核心稳定和协调训练",
                        instructions: "仰卧，对侧手脚交替伸展",
                        form_cues: ["保持下背部贴地", "动作缓慢控制", "对侧协调"],
                        sets_reps: "3组 x 10次/侧",
                        rest_time: "60秒"
                    },
                    {
                        name: "山地跑",
                        english_name: "Mountain Climbers",
                        difficulty: "intermediate",
                        type: "compound",
                        primary_muscles: ["腹直肌", "腹斜肌"],
                        secondary_muscles: ["肩部", "腿部"],
                        equipment: ["自重"],
                        description: "动态核心和有氧结合训练",
                        instructions: "俯卧撑姿势，双腿交替向胸部靠近",
                        form_cues: ["保持臀部高度", "核心收紧", "动作快速"],
                        sets_reps: "3组 x 20-30次",
                        rest_time: "60秒"
                    }
                ]
            };
        } catch (error) {
            console.error('加载动作库失败:', error);
        }
    }

    async loadTemplates() {
        try {
            const response = await fetch('/api/fitness/training-plan-templates/');
            if (response.ok) {
                this.templates = await response.json();
            }
        } catch (error) {
            console.error('加载模板失败:', error);
            // 使用默认模板
            this.templates = this.getDefaultTemplates();
        }
    }

    getDefaultTemplates() {
        return {
            "五分化": {
                name: "五分化力量训练",
                description: "经典五分化训练，适合中高级训练者",
                schedule: [
                    { weekday: "周一", body_parts: ["胸部"], focus: "胸部专项训练" },
                    { weekday: "周二", body_parts: ["背部"], focus: "背部专项训练" },
                    { weekday: "周三", body_parts: ["休息"], focus: "休息恢复" },
                    { weekday: "周四", body_parts: ["肩部"], focus: "肩部专项训练" },
                    { weekday: "周五", body_parts: ["腿部"], focus: "腿部专项训练" },
                    { weekday: "周六", body_parts: ["手臂"], focus: "手臂专项训练" },
                    { weekday: "周日", body_parts: ["休息"], focus: "休息恢复" }
                ]
            },
            "推拉腿": {
                name: "推拉腿训练",
                description: "按推拉腿模式划分的高效训练",
                schedule: [
                    { weekday: "周一", body_parts: ["推"], focus: "胸部、肩部、三头肌" },
                    { weekday: "周二", body_parts: ["拉"], focus: "背部、二头肌" },
                    { weekday: "周三", body_parts: ["腿"], focus: "腿部、臀部" },
                    { weekday: "周四", body_parts: ["推"], focus: "胸部、肩部、三头肌" },
                    { weekday: "周五", body_parts: ["拉"], focus: "背部、二头肌" },
                    { weekday: "周六", body_parts: ["腿"], focus: "腿部、臀部" },
                    { weekday: "周日", body_parts: ["休息"], focus: "休息恢复" }
                ]
            },
            "全身训练": {
                name: "全身训练",
                description: "适合初学者的全身训练计划",
                schedule: [
                    { weekday: "周一", body_parts: ["全身"], focus: "全身基础训练" },
                    { weekday: "周二", body_parts: ["休息"], focus: "休息恢复" },
                    { weekday: "周三", body_parts: ["全身"], focus: "全身基础训练" },
                    { weekday: "周四", body_parts: ["休息"], focus: "休息恢复" },
                    { weekday: "周五", body_parts: ["全身"], focus: "全身基础训练" },
                    { weekday: "周六", body_parts: ["休息"], focus: "休息恢复" },
                    { weekday: "周日", body_parts: ["休息"], focus: "休息恢复" }
                ]
            }
        };
    }

    renderDayTabs() {
        const tabsContainer = document.querySelector('.day-tabs');
        if (!tabsContainer) return;

        tabsContainer.innerHTML = '';
        
        this.planData.week_schedule.forEach((day, index) => {
            const tab = document.createElement('div');
            tab.className = `day-tab ${index === this.currentDay ? 'active' : ''}`;
            tab.innerHTML = `
                <div class="tab-day">${day.weekday}</div>
                <div class="tab-parts">${day.body_parts.join(', ')}</div>
            `;
            tab.addEventListener('click', () => this.switchDay(index));
            tabsContainer.appendChild(tab);
        });
    }

    renderCurrentDay() {
        const dayContent = document.querySelector('.day-content');
        if (!dayContent) return;

        const currentDay = this.planData.week_schedule[this.currentDay];
        
        dayContent.innerHTML = `
            <div class="day-header">
                <h3>${currentDay.weekday} - ${currentDay.body_parts.join(', ')}</h3>
                <div class="day-actions">
                    <button class="btn-secondary" onclick="trainingEditor.copyDay()">
                        <i class="fas fa-copy"></i> 复制训练
                    </button>
                    <button class="btn-secondary" onclick="trainingEditor.clearDay()">
                        <i class="fas fa-trash"></i> 清空训练
                    </button>
                </div>
            </div>
            
            <div class="training-modules">
                ${this.renderModule('warmup', '热身', currentDay.modules.warmup)}
                ${this.renderModule('main', '主要训练', currentDay.modules.main)}
                ${this.renderModule('accessory', '辅助训练', currentDay.modules.accessory)}
                ${this.renderModule('cooldown', '放松整理', currentDay.modules.cooldown)}
            </div>
        `;
    }

    renderModule(moduleType, moduleName, exercises) {
        return `
            <div class="training-module" data-module="${moduleType}">
                <div class="module-header">
                    <h4><i class="fas fa-dumbbell"></i> ${moduleName}</h4>
                    <span class="exercise-count">${exercises.length} 个动作</span>
                </div>
                <div class="module-exercises" data-module="${moduleType}">
                    ${exercises.map((exercise, index) => this.renderExerciseCard(exercise, moduleType, index)).join('')}
                    <div class="add-exercise-card" onclick="trainingEditor.showExerciseSelector('${moduleType}')">
                        <i class="fas fa-plus"></i>
                        <span>添加动作</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderExerciseCard(exercise, moduleType, index) {
        const difficultyColor = this.getDifficultyColor(exercise.difficulty);
        const typeIcon = this.getExerciseTypeIcon(exercise.type);
        
        return `
            <div class="exercise-card" data-exercise-index="${index}">
                <div class="exercise-header">
                    <div class="exercise-name">
                        <i class="${typeIcon}"></i>
                        <span class="name">${exercise.name}</span>
                        ${exercise.english_name ? `<span class="english-name">${exercise.english_name}</span>` : ''}
                    </div>
                    <div class="exercise-actions">
                        <button class="btn-icon" onclick="trainingEditor.showExerciseDetail('${exercise.name}')" title="查看详情">
                            <i class="fas fa-info-circle"></i>
                        </button>
                        <button class="btn-icon" onclick="trainingEditor.removeExercise('${moduleType}', ${index})" title="移除">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                
                <div class="exercise-details">
                    <div class="exercise-meta">
                        <span class="difficulty" style="color: ${difficultyColor}">
                            <i class="fas fa-star"></i> ${this.getDifficultyText(exercise.difficulty)}
                        </span>
                        <span class="muscles">
                            <i class="fas fa-crosshairs"></i> ${exercise.primary_muscles ? exercise.primary_muscles.join(', ') : ''}
                        </span>
                    </div>
                    
                    <div class="exercise-params">
                        <div class="param-group">
                            <label>组数</label>
                            <input type="text" value="${exercise.sets || '3'}" 
                                   onchange="trainingEditor.updateExerciseParam('${moduleType}', ${index}, 'sets', this.value)">
                        </div>
                        <div class="param-group">
                            <label>次数</label>
                            <input type="text" value="${exercise.reps || '8-12'}" 
                                   onchange="trainingEditor.updateExerciseParam('${moduleType}', ${index}, 'reps', this.value)">
                        </div>
                        <div class="param-group">
                            <label>休息</label>
                            <input type="text" value="${exercise.rest || '90秒'}" 
                                   onchange="trainingEditor.updateExerciseParam('${moduleType}', ${index}, 'rest', this.value)">
                        </div>
                    </div>
                    
                    ${exercise.notes ? `<div class="exercise-notes">${exercise.notes}</div>` : ''}
                </div>
            </div>
        `;
    }

    renderExerciseLibrary() {
        const libraryContainer = document.querySelector('.exercise-library .body-parts');
        if (!libraryContainer) return;

        libraryContainer.innerHTML = '';

        Object.entries(this.exerciseLibrary).forEach(([bodyPart, exercises]) => {
            const bodyPartSection = document.createElement('div');
            bodyPartSection.className = 'body-part-section';
            bodyPartSection.innerHTML = `
                <div class="body-part-header" onclick="this.parentElement.classList.toggle('collapsed')">
                    <h4><i class="fas fa-chevron-down"></i> ${this.getBodyPartName(bodyPart)}</h4>
                    <span class="exercise-count">${exercises.length} 个动作</span>
                </div>
                <div class="exercise-list">
                    ${exercises.map(exercise => this.renderLibraryExercise(exercise)).join('')}
                </div>
            `;
            libraryContainer.appendChild(bodyPartSection);
        });
    }

    renderLibraryExercise(exercise) {
        const difficultyColor = this.getDifficultyColor(exercise.difficulty);
        const typeIcon = this.getExerciseTypeIcon(exercise.type);
        
        return `
            <div class="library-exercise" draggable="true" 
                 data-exercise='${JSON.stringify(exercise)}'
                 ondragstart="trainingEditor.handleDragStart(event)">
                <div class="exercise-info">
                    <div class="exercise-name">
                        <i class="${typeIcon}"></i>
                        <span class="name">${exercise.name}</span>
                        ${exercise.english_name ? `<small class="english-name">${exercise.english_name}</small>` : ''}
                    </div>
                    <div class="exercise-meta">
                        <span class="difficulty" style="color: ${difficultyColor}">
                            ${this.getDifficultyText(exercise.difficulty)}
                        </span>
                        <span class="type">${this.getExerciseTypeText(exercise.type)}</span>
                    </div>
                    <div class="exercise-muscles">
                        <i class="fas fa-crosshairs"></i> 
                        ${exercise.primary_muscles ? exercise.primary_muscles.join(', ') : ''}
                    </div>
                    <div class="exercise-equipment">
                        <i class="fas fa-tools"></i> 
                        ${exercise.equipment ? exercise.equipment.join(', ') : '自重'}
                    </div>
                </div>
                <div class="exercise-actions">
                    <button class="btn-icon" onclick="trainingEditor.showExerciseDetail('${exercise.name}')" title="查看详情">
                        <i class="fas fa-info-circle"></i>
                    </button>
                    <button class="btn-icon" onclick="trainingEditor.toggleFavorite('${exercise.name}')" title="收藏">
                        <i class="far fa-heart"></i>
                    </button>
                </div>
            </div>
        `;
    }

    bindEvents() {
        // 绑定拖拽事件
        this.bindDragDropEvents();
        
        // 绑定搜索事件
        const searchInput = document.getElementById('exerciseSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.searchExercises(e.target.value));
        }
        
        // 绑定保存事件
        const saveBtn = document.getElementById('savePlan');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.savePlan());
        }
        
        // 绑定模板选择事件
        const templateBtn = document.getElementById('selectTemplate');
        if (templateBtn) {
            templateBtn.addEventListener('click', () => this.showTemplateModal());
        }
        
        // 监听窗口关闭事件
        window.addEventListener('beforeunload', (e) => {
            if (this.isDirty) {
                e.preventDefault();
                e.returnValue = '您有未保存的更改，确定要离开吗？';
            }
        });
    }

    bindDragDropEvents() {
        // 为训练模块绑定拖拽目标事件
        document.querySelectorAll('.module-exercises').forEach(module => {
            module.addEventListener('dragover', this.handleDragOver.bind(this));
            module.addEventListener('drop', this.handleDrop.bind(this));
        });
    }

    handleDragStart(event) {
        const exerciseData = event.target.getAttribute('data-exercise');
        event.dataTransfer.setData('text/plain', exerciseData);
        event.dataTransfer.effectAllowed = 'copy';
    }

    handleDragOver(event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'copy';
        event.target.classList.add('drag-over');
    }

    handleDrop(event) {
        event.preventDefault();
        event.target.classList.remove('drag-over');
        
        const exerciseData = event.dataTransfer.getData('text/plain');
        const exercise = JSON.parse(exerciseData);
        const moduleType = event.target.getAttribute('data-module');
        
        this.addExerciseToModule(exercise, moduleType);
    }

    addExerciseToModule(exercise, moduleType) {
        const currentDay = this.planData.week_schedule[this.currentDay];
        
        // 添加默认训练参数
        const exerciseWithParams = {
            ...exercise,
            sets: exercise.sets_reps ? exercise.sets_reps.split(' x ')[0] : '3',
            reps: exercise.sets_reps ? exercise.sets_reps.split(' x ')[1] : '8-12',
            rest: exercise.rest_time || '90秒'
        };
        
        currentDay.modules[moduleType].push(exerciseWithParams);
        this.markDirty();
        this.renderCurrentDay();
        this.bindDragDropEvents(); // 重新绑定事件
    }

    removeExercise(moduleType, index) {
        const currentDay = this.planData.week_schedule[this.currentDay];
        currentDay.modules[moduleType].splice(index, 1);
        this.markDirty();
        this.renderCurrentDay();
        this.bindDragDropEvents();
    }

    updateExerciseParam(moduleType, index, param, value) {
        const currentDay = this.planData.week_schedule[this.currentDay];
        currentDay.modules[moduleType][index][param] = value;
        this.markDirty();
    }

    switchDay(dayIndex) {
        this.currentDay = dayIndex;
        this.renderDayTabs();
        this.renderCurrentDay();
        this.bindDragDropEvents();
    }

    showTemplateModal() {
        const modal = document.getElementById('templateModal');
        if (modal) {
            modal.style.display = 'block';
            this.renderTemplateOptions();
        }
    }

    renderTemplateOptions() {
        const templateGrid = document.querySelector('.template-grid');
        if (!templateGrid) return;

        templateGrid.innerHTML = '';
        
        Object.entries(this.templates).forEach(([key, template]) => {
            const templateCard = document.createElement('div');
            templateCard.className = 'template-card';
            templateCard.innerHTML = `
                <div class="template-icon">
                    <i class="fas fa-dumbbell"></i>
                </div>
                <div class="template-info">
                    <h4>${template.name}</h4>
                    <p>${template.description}</p>
                    <div class="template-schedule">
                        ${template.schedule.slice(0, 3).map(day => 
                            `<span class="schedule-day">${day.weekday}: ${day.body_parts.join(', ')}</span>`
                        ).join('')}
                        ${template.schedule.length > 3 ? '<span class="more">...</span>' : ''}
                    </div>
                </div>
            `;
            templateCard.addEventListener('click', () => this.selectTemplate(key));
            templateGrid.appendChild(templateCard);
        });
    }

    selectTemplate(templateKey) {
        const template = this.templates[templateKey];
        if (!template) return;

        // 应用模板到当前计划
        this.planData.week_schedule = template.schedule.map(day => ({
            weekday: day.weekday,
            body_parts: day.body_parts,
            modules: { warmup: [], main: [], accessory: [], cooldown: [] }
        }));

        // 根据身体部位自动添加推荐动作
        this.planData.week_schedule.forEach(day => {
            if (day.body_parts.includes('休息')) return;
            
            day.body_parts.forEach(bodyPart => {
                const bodyPartKey = this.getBodyPartKey(bodyPart);
                if (this.exerciseLibrary[bodyPartKey]) {
                    // 添加2-3个主要动作
                    const mainExercises = this.exerciseLibrary[bodyPartKey]
                        .filter(ex => ex.type === 'compound')
                        .slice(0, 2);
                    
                    mainExercises.forEach(exercise => {
                        day.modules.main.push({
                            ...exercise,
                            sets: '3',
                            reps: '8-12',
                            rest: '90秒'
                        });
                    });
                    
                    // 添加1个辅助动作
                    const accessoryExercise = this.exerciseLibrary[bodyPartKey]
                        .find(ex => ex.type === 'isolation');
                    
                    if (accessoryExercise) {
                        day.modules.accessory.push({
                            ...accessoryExercise,
                            sets: '3',
                            reps: '12-15',
                            rest: '60秒'
                        });
                    }
                }
            });
        });

        this.markDirty();
        this.renderDayTabs();
        this.renderCurrentDay();
        this.bindDragDropEvents();
        this.closeTemplateModal();
        
        // 显示成功消息
        this.showMessage('模板应用成功！', 'success');
    }

    closeTemplateModal() {
        const modal = document.getElementById('templateModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    searchExercises(query) {
        const libraryContainer = document.querySelector('.exercise-library .body-parts');
        if (!libraryContainer) return;

        if (!query.trim()) {
            this.renderExerciseLibrary();
            return;
        }

        const filteredExercises = {};
        Object.entries(this.exerciseLibrary).forEach(([bodyPart, exercises]) => {
            const filtered = exercises.filter(exercise => 
                exercise.name.toLowerCase().includes(query.toLowerCase()) ||
                (exercise.english_name && exercise.english_name.toLowerCase().includes(query.toLowerCase())) ||
                (exercise.primary_muscles && exercise.primary_muscles.some(muscle => 
                    muscle.toLowerCase().includes(query.toLowerCase())
                ))
            );
            
            if (filtered.length > 0) {
                filteredExercises[bodyPart] = filtered;
            }
        });

        // 渲染搜索结果
        libraryContainer.innerHTML = '';
        if (Object.keys(filteredExercises).length === 0) {
            libraryContainer.innerHTML = '<div class="no-results">未找到匹配的动作</div>';
            return;
        }

        Object.entries(filteredExercises).forEach(([bodyPart, exercises]) => {
            const bodyPartSection = document.createElement('div');
            bodyPartSection.className = 'body-part-section';
            bodyPartSection.innerHTML = `
                <div class="body-part-header">
                    <h4><i class="fas fa-search"></i> ${this.getBodyPartName(bodyPart)}</h4>
                    <span class="exercise-count">${exercises.length} 个动作</span>
                </div>
                <div class="exercise-list">
                    ${exercises.map(exercise => this.renderLibraryExercise(exercise)).join('')}
                </div>
            `;
            libraryContainer.appendChild(bodyPartSection);
        });
    }

    showExerciseDetail(exerciseName) {
        // 查找动作详情
        let exercise = null;
        Object.values(this.exerciseLibrary).forEach(exercises => {
            const found = exercises.find(ex => ex.name === exerciseName);
            if (found) exercise = found;
        });

        if (!exercise) return;

        // 创建详情模态框
        const modal = document.createElement('div');
        modal.className = 'modal exercise-detail-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${exercise.name}</h3>
                    ${exercise.english_name ? `<p class="english-name">${exercise.english_name}</p>` : ''}
                    <button class="close-btn" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="exercise-detail-content">
                        <div class="detail-section">
                            <h4><i class="fas fa-info-circle"></i> 基本信息</h4>
                            <div class="detail-grid">
                                <div class="detail-item">
                                    <label>难度等级</label>
                                    <span class="difficulty" style="color: ${this.getDifficultyColor(exercise.difficulty)}">
                                        ${this.getDifficultyText(exercise.difficulty)}
                                    </span>
                                </div>
                                <div class="detail-item">
                                    <label>动作类型</label>
                                    <span>${this.getExerciseTypeText(exercise.type)}</span>
                                </div>
                                <div class="detail-item">
                                    <label>主要肌群</label>
                                    <span>${exercise.primary_muscles ? exercise.primary_muscles.join(', ') : ''}</span>
                                </div>
                                <div class="detail-item">
                                    <label>辅助肌群</label>
                                    <span>${exercise.secondary_muscles ? exercise.secondary_muscles.join(', ') : '无'}</span>
                                </div>
                                <div class="detail-item">
                                    <label>所需器械</label>
                                    <span>${exercise.equipment ? exercise.equipment.join(', ') : '自重'}</span>
                                </div>
                                <div class="detail-item">
                                    <label>推荐参数</label>
                                    <span>${exercise.sets_reps || '3组 x 8-12次'}</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="detail-section">
                            <h4><i class="fas fa-clipboard-list"></i> 动作描述</h4>
                            <p>${exercise.description}</p>
                        </div>
                        
                        <div class="detail-section">
                            <h4><i class="fas fa-play-circle"></i> 执行要领</h4>
                            <p>${exercise.instructions}</p>
                        </div>
                        
                        ${exercise.form_cues && exercise.form_cues.length > 0 ? `
                        <div class="detail-section">
                            <h4><i class="fas fa-bullseye"></i> 技术要点</h4>
                            <ul>
                                ${exercise.form_cues.map(cue => `<li>${cue}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="this.closest('.modal').remove()">关闭</button>
                    <button class="btn-primary" onclick="trainingEditor.addExerciseFromDetail('${exercise.name}')">
                        <i class="fas fa-plus"></i> 添加到训练
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.style.display = 'block';
    }

    addExerciseFromDetail(exerciseName) {
        // 查找动作
        let exercise = null;
        Object.values(this.exerciseLibrary).forEach(exercises => {
            const found = exercises.find(ex => ex.name === exerciseName);
            if (found) exercise = found;
        });

        if (!exercise) return;

        // 显示模块选择
        const moduleSelector = document.createElement('div');
        moduleSelector.className = 'module-selector';
        moduleSelector.innerHTML = `
            <div class="selector-content">
                <h4>选择训练模块</h4>
                <div class="module-options">
                    <button class="module-option" onclick="trainingEditor.addToModule('${exerciseName}', 'warmup')">
                        <i class="fas fa-fire"></i> 热身
                    </button>
                    <button class="module-option" onclick="trainingEditor.addToModule('${exerciseName}', 'main')">
                        <i class="fas fa-dumbbell"></i> 主要训练
                    </button>
                    <button class="module-option" onclick="trainingEditor.addToModule('${exerciseName}', 'accessory')">
                        <i class="fas fa-plus-circle"></i> 辅助训练
                    </button>
                    <button class="module-option" onclick="trainingEditor.addToModule('${exerciseName}', 'cooldown')">
                        <i class="fas fa-leaf"></i> 放松整理
                    </button>
                </div>
            </div>
        `;
        
        document.querySelector('.exercise-detail-modal .modal-body').appendChild(moduleSelector);
    }

    addToModule(exerciseName, moduleType) {
        // 查找动作
        let exercise = null;
        Object.values(this.exerciseLibrary).forEach(exercises => {
            const found = exercises.find(ex => ex.name === exerciseName);
            if (found) exercise = found;
        });

        if (exercise) {
            this.addExerciseToModule(exercise, moduleType);
            document.querySelector('.exercise-detail-modal').remove();
            this.showMessage(`已添加 "${exercise.name}" 到${this.getModuleName(moduleType)}`, 'success');
        }
    }

    async savePlan() {
        try {
            const planName = document.getElementById('planName')?.value || this.planData.name;
            const planDescription = document.getElementById('planDescription')?.value || this.planData.description;
            
            const planData = {
                ...this.planData,
                name: planName,
                description: planDescription
            };

            const response = await fetch('/api/fitness/save-custom-plan/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(planData)
            });

            const result = await response.json();
            
            if (result.success) {
                this.isDirty = false;
                this.showMessage('训练计划保存成功！', 'success');
                
                // 可选：跳转到计划详情页面
                if (result.plan_id) {
                    setTimeout(() => {
                        window.location.href = `/fitness/plan/${result.plan_id}/`;
                    }, 1500);
                }
            } else {
                this.showMessage('保存失败：' + result.error, 'error');
            }
        } catch (error) {
            console.error('保存计划失败:', error);
            this.showMessage('保存失败，请重试', 'error');
        }
    }

    autoSave() {
        // 自动保存到本地存储
        try {
            localStorage.setItem('fitness_plan_draft', JSON.stringify(this.planData));

        } catch (error) {
            console.error('自动保存失败:', error);
        }
    }

    loadDraft() {
        // 加载草稿
        try {
            const draft = localStorage.getItem('fitness_plan_draft');
            if (draft) {
                const confirmed = confirm('发现未保存的草稿，是否加载？');
                if (confirmed) {
                    this.planData = JSON.parse(draft);
                    this.renderDayTabs();
                    this.renderCurrentDay();
                    this.bindDragDropEvents();
                }
            }
        } catch (error) {
            console.error('加载草稿失败:', error);
        }
    }

    markDirty() {
        this.isDirty = true;
        // 更新页面标题提示
        if (!document.title.includes('*')) {
            document.title = '* ' + document.title;
        }
    }

    // 工具方法
    getDifficultyColor(difficulty) {
        const colors = {
            'beginner': '#28a745',
            'intermediate': '#ffc107',
            'advanced': '#fd7e14',
            'expert': '#dc3545'
        };
        return colors[difficulty] || '#6c757d';
    }

    getDifficultyText(difficulty) {
        const texts = {
            'beginner': '初学者',
            'intermediate': '中级',
            'advanced': '高级',
            'expert': '专家'
        };
        return texts[difficulty] || difficulty;
    }

    getExerciseTypeIcon(type) {
        const icons = {
            'compound': 'fas fa-arrows-alt',
            'isolation': 'fas fa-crosshairs',
            'cardio': 'fas fa-running',
            'isometric': 'fas fa-pause'
        };
        return icons[type] || 'fas fa-dumbbell';
    }

    getExerciseTypeText(type) {
        const texts = {
            'compound': '复合动作',
            'isolation': '孤立动作',
            'cardio': '有氧运动',
            'isometric': '等长收缩'
        };
        return texts[type] || type;
    }

    getBodyPartName(bodyPart) {
        const names = {
            'chest': '胸部',
            'back': '背部',
            'shoulders': '肩部',
            'legs': '腿部',
            'arms': '手臂',
            'core': '核心'
        };
        return names[bodyPart] || bodyPart;
    }

    getBodyPartKey(bodyPartName) {
        const keys = {
            '胸部': 'chest',
            '背部': 'back',
            '肩部': 'shoulders',
            '腿部': 'legs',
            '手臂': 'arms',
            '核心': 'core',
            '推': 'chest', // 推日主要是胸部
            '拉': 'back',  // 拉日主要是背部
            '全身': 'chest' // 全身训练从胸部开始
        };
        return keys[bodyPartName] || 'chest';
    }

    getModuleName(moduleType) {
        const names = {
            'warmup': '热身',
            'main': '主要训练',
            'accessory': '辅助训练',
            'cooldown': '放松整理'
        };
        return names[moduleType] || moduleType;
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    showMessage(message, type = 'info') {
        // 创建消息提示
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        messageDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(messageDiv);
        
        // 自动消失
        setTimeout(() => {
            messageDiv.classList.add('fade-out');
            setTimeout(() => messageDiv.remove(), 300);
        }, 3000);
    }

    // 复制和清空功能
    copyDay() {
        const currentDay = this.planData.week_schedule[this.currentDay];
        this.copiedDay = JSON.parse(JSON.stringify(currentDay));
        this.showMessage('已复制当天训练', 'success');
    }

    pasteDay() {
        if (!this.copiedDay) {
            this.showMessage('没有可粘贴的训练', 'warning');
            return;
        }
        
        const currentDay = this.planData.week_schedule[this.currentDay];
        currentDay.modules = JSON.parse(JSON.stringify(this.copiedDay.modules));
        
        this.markDirty();
        this.renderCurrentDay();
        this.bindDragDropEvents();
        this.showMessage('已粘贴训练', 'success');
    }

    clearDay() {
        const confirmed = confirm('确定要清空当天的所有训练吗？');
        if (!confirmed) return;
        
        const currentDay = this.planData.week_schedule[this.currentDay];
        currentDay.modules = { warmup: [], main: [], accessory: [], cooldown: [] };
        
        this.markDirty();
        this.renderCurrentDay();
        this.bindDragDropEvents();
        this.showMessage('已清空当天训练', 'success');
    }

    toggleFavorite(exerciseName) {
        // 发送收藏请求到后端
        fetch('/api/fitness/toggle-exercise-favorite/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({ exercise_name: exerciseName })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                this.showMessage(
                    result.is_favorite ? '已添加到收藏' : '已取消收藏',
                    'success'
                );
            }
        })
        .catch(error => {
            console.error('收藏操作失败:', error);
        });
    }
}

// 初始化训练计划编辑器
let trainingEditor;
document.addEventListener('DOMContentLoaded', function() {
    trainingEditor = new EnhancedTrainingPlanEditor();
    
    // 加载草稿
    trainingEditor.loadDraft();
});

// 导出供全局使用
window.trainingEditor = trainingEditor;
