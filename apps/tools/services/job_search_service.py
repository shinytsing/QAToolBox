import requests
import json
import time
import random
from typing import List, Dict, Optional
from django.conf import settings
from django.utils import timezone
from ..models import JobSearchRequest, JobApplication, JobSearchProfile


class BossZhipinAPI:
    """Boss直聘API服务类"""
    
    def __init__(self):
        self.base_url = "https://www.zhipin.com"
        self.api_url = "https://www.zhipin.com/api"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search_jobs(self, 
                   job_title: str, 
                   location: str, 
                   min_salary: int, 
                   max_salary: int,
                   job_type: str = 'full_time',
                   experience_level: str = '1-3',
                   keywords: List[str] = None,
                   page: int = 1,
                   page_size: int = 30) -> Dict:
        """
        搜索职位
        """
        try:
            # 构建搜索参数
            search_params = {
                'query': job_title,
                'city': location,
                'salary_min': min_salary * 1000,  # 转换为元
                'salary_max': max_salary * 1000,
                'page': page,
                'pageSize': page_size,
                'jobType': self._convert_job_type(job_type),
                'experience': self._convert_experience(experience_level),
            }
            
            if keywords:
                search_params['keywords'] = ','.join(keywords)
            
            # 模拟API调用（实际项目中需要真实的Boss直聘API）
            return self._mock_search_results(search_params)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
    
    def apply_job(self, job_id: str, user_profile: JobSearchProfile) -> Dict:
        """
        投递简历到指定职位
        """
        try:
            # 模拟投递过程
            time.sleep(random.uniform(1, 3))  # 模拟网络延迟
            
            # 模拟成功率
            success_rate = random.uniform(0.7, 0.95)
            is_success = random.random() < success_rate
            
            if is_success:
                return {
                    'success': True,
                    'message': '投递成功',
                    'application_id': f'app_{job_id}_{int(time.time())}',
                    'status': 'applied'
                }
            else:
                return {
                    'success': False,
                    'message': '投递失败，请稍后重试',
                    'status': 'failed'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status': 'error'
            }
    
    def get_job_details(self, job_id: str) -> Dict:
        """
        获取职位详情
        """
        try:
            # 模拟职位详情数据
            return self._mock_job_details(job_id)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def _convert_job_type(self, job_type: str) -> str:
        """转换工作类型"""
        type_mapping = {
            'full_time': '1',
            'part_time': '2',
            'internship': '3',
            'freelance': '4'
        }
        return type_mapping.get(job_type, '1')
    
    def _convert_experience(self, experience: str) -> str:
        """转换经验要求"""
        exp_mapping = {
            'fresh': '1',
            '1-3': '2',
            '3-5': '3',
            '5-10': '4',
            '10+': '5'
        }
        return exp_mapping.get(experience, '2')
    
    def _mock_search_results(self, params: Dict) -> Dict:
        """模拟搜索结果"""
        job_titles = [
            'Python开发工程师', '前端开发工程师', 'Java开发工程师', 
            '数据分析师', '产品经理', 'UI设计师', '运维工程师',
            '测试工程师', '算法工程师', '架构师'
        ]
        
        companies = [
            '腾讯科技', '阿里巴巴', '字节跳动', '百度', '美团',
            '滴滴出行', '京东科技', '网易', '小米科技', '华为'
        ]
        
        locations = ['北京', '上海', '深圳', '广州', '杭州', '成都', '南京', '武汉']
        
        results = []
        for i in range(params.get('pageSize', 30)):
            job = {
                'id': f'job_{params["page"]}_{i}',
                'title': random.choice(job_titles),
                'company': random.choice(companies),
                'location': random.choice(locations),
                'salary_min': params['salary_min'] // 1000,
                'salary_max': params['salary_max'] // 1000,
                'experience': params.get('experience', '2'),
                'education': random.choice(['本科', '硕士', '博士']),
                'company_size': random.choice(['100-499人', '500-999人', '1000-9999人', '10000人以上']),
                'industry': random.choice(['互联网', '金融', '教育', '医疗', '电商']),
                'description': f'这是一个{random.choice(job_titles)}的职位，要求有相关工作经验...',
                'requirements': ['熟悉相关技术栈', '有团队协作能力', '良好的沟通能力'],
                'benefits': ['五险一金', '年终奖', '带薪年假', '免费午餐'],
                'url': f'https://www.zhipin.com/job_detail/{params["page"]}_{i}.html',
                'logo': f'https://img.bosszhipin.com/company_logo/logo_{i}.png'
            }
            results.append(job)
        
        return {
            'success': True,
            'data': {
                'jobs': results,
                'total': 150,
                'page': params['page'],
                'pageSize': params['pageSize']
            }
        }
    
    def _mock_job_details(self, job_id: str) -> Dict:
        """模拟职位详情"""
        return {
            'success': True,
            'data': {
                'id': job_id,
                'title': 'Python开发工程师',
                'company': '腾讯科技',
                'location': '深圳',
                'salary_range': '15K-30K',
                'experience': '3-5年',
                'education': '本科及以上',
                'description': '负责公司核心产品的后端开发工作...',
                'requirements': [
                    '熟悉Python编程语言',
                    '熟悉Django/Flask等Web框架',
                    '熟悉MySQL、Redis等数据库',
                    '有良好的代码规范和团队协作能力'
                ],
                'benefits': [
                    '五险一金',
                    '年终奖',
                    '带薪年假',
                    '免费午餐',
                    '定期团建'
                ]
            }
        }


class JobSearchService:
    """求职服务主类"""
    
    def __init__(self):
        self.boss_api = BossZhipinAPI()
    
    def create_job_search_request(self, user, **kwargs) -> JobSearchRequest:
        """创建求职请求"""
        try:
            job_request = JobSearchRequest.objects.create(
                user=user,
                **kwargs
            )
            return job_request
        except Exception as e:
            raise Exception(f"创建求职请求失败: {str(e)}")
    
    def start_auto_job_search(self, job_request: JobSearchRequest) -> Dict:
        """开始自动求职"""
        try:
            # 更新状态为处理中
            job_request.status = 'processing'
            job_request.save()
            
            # 获取用户资料
            try:
                user_profile = JobSearchProfile.objects.get(user=job_request.user)
            except JobSearchProfile.DoesNotExist:
                job_request.status = 'failed'
                job_request.error_message = '请先完善求职者资料'
                job_request.save()
                return {'success': False, 'message': '请先完善求职者资料'}
            
            # 开始搜索和投递
            total_found = 0
            total_applied = 0
            
            for page in range(1, 6):  # 搜索前5页
                # 搜索职位
                search_result = self.boss_api.search_jobs(
                    job_title=job_request.job_title,
                    location=job_request.location,
                    min_salary=job_request.min_salary,
                    max_salary=job_request.max_salary,
                    job_type=job_request.job_type,
                    experience_level=job_request.experience_level,
                    keywords=job_request.keywords,
                    page=page
                )
                
                if not search_result.get('success'):
                    continue
                
                jobs = search_result['data']['jobs']
                total_found += len(jobs)
                
                # 筛选和投递
                for job in jobs:
                    if total_applied >= job_request.max_applications:
                        break
                    
                    # 计算匹配度
                    match_score = self._calculate_match_score(job, job_request, user_profile)
                    
                    # 如果匹配度达到60%以上，进行投递
                    if match_score >= 60:
                        # 投递简历
                        apply_result = self.boss_api.apply_job(job['id'], user_profile)
                        
                        if apply_result.get('success'):
                            # 创建申请记录
                            JobApplication.objects.create(
                                job_search_request=job_request,
                                job_id=job['id'],
                                job_title=job['title'],
                                company_name=job['company'],
                                company_logo=job.get('logo', ''),
                                location=job['location'],
                                salary_range=f"{job['salary_min']}K-{job['salary_max']}K",
                                job_description=job.get('description', ''),
                                requirements=job.get('requirements', []),
                                benefits=job.get('benefits', []),
                                status='applied',
                                platform='boss',
                                job_url=job['url'],
                                match_score=match_score,
                                match_reasons=self._get_match_reasons(job, job_request, user_profile)
                            )
                            
                            total_applied += 1
                            
                            # 更新用户统计
                            user_profile.total_applications += 1
                            user_profile.save()
                            
                            # 等待间隔时间
                            time.sleep(job_request.application_interval)
                
                if total_applied >= job_request.max_applications:
                    break
            
            # 更新请求状态
            job_request.status = 'completed'
            job_request.total_jobs_found = total_found
            job_request.total_applications_sent = total_applied
            job_request.success_rate = (total_applied / max(total_found, 1)) * 100
            job_request.completed_at = timezone.now()
            job_request.save()
            
            return {
                'success': True,
                'message': f'自动求职完成！找到{total_found}个职位，成功投递{total_applied}份简历',
                'total_found': total_found,
                'total_applied': total_applied
            }
            
        except Exception as e:
            job_request.status = 'failed'
            job_request.error_message = str(e)
            job_request.save()
            return {'success': False, 'message': f'自动求职失败: {str(e)}'}
    
    def _calculate_match_score(self, job: Dict, job_request: JobSearchRequest, user_profile: JobSearchProfile) -> float:
        """计算职位匹配度"""
        score = 0
        
        # 薪资匹配度 (30%)
        job_salary_avg = (job['salary_min'] + job['salary_max']) / 2
        request_salary_avg = (job_request.min_salary + job_request.max_salary) / 2
        
        if job_salary_avg >= job_request.min_salary and job_salary_avg <= job_request.max_salary:
            score += 30
        elif job_salary_avg >= job_request.min_salary * 0.8:
            score += 20
        elif job_salary_avg >= job_request.min_salary * 0.6:
            score += 10
        
        # 地点匹配度 (25%)
        if job['location'] in job_request.location:
            score += 25
        elif any(city in job['location'] for city in user_profile.preferred_locations):
            score += 15
        
        # 经验匹配度 (20%)
        experience_match = {
            'fresh': ['应届生', '无经验'],
            '1-3': ['1-3年', '初级'],
            '3-5': ['3-5年', '中级'],
            '5-10': ['5-10年', '高级'],
            '10+': ['10年以上', '专家']
        }
        
        if job_request.experience_level in experience_match:
            if any(exp in str(job.get('experience', '')) for exp in experience_match[job_request.experience_level]):
                score += 20
        
        # 技能匹配度 (15%)
        user_skills = set(user_profile.skills)
        job_requirements = set(job.get('requirements', []))
        if user_skills and job_requirements:
            skill_match = len(user_skills.intersection(job_requirements)) / len(job_requirements)
            score += skill_match * 15
        
        # 公司规模匹配度 (10%)
        if job.get('company_size') in ['1000-9999人', '10000人以上']:
            score += 10
        
        return min(100, score)
    
    def _get_match_reasons(self, job: Dict, job_request: JobSearchRequest, user_profile: JobSearchProfile) -> List[str]:
        """获取匹配原因"""
        reasons = []
        
        # 薪资匹配
        job_salary_avg = (job['salary_min'] + job['salary_max']) / 2
        if job_salary_avg >= job_request.min_salary:
            reasons.append('薪资符合期望')
        
        # 地点匹配
        if job['location'] in job_request.location:
            reasons.append('工作地点符合')
        
        # 技能匹配
        user_skills = set(user_profile.skills)
        job_requirements = set(job.get('requirements', []))
        if user_skills and job_requirements:
            common_skills = user_skills.intersection(job_requirements)
            if common_skills:
                reasons.append(f'技能匹配: {", ".join(list(common_skills)[:3])}')
        
        return reasons
    
    def get_job_search_statistics(self, user) -> Dict:
        """获取求职统计信息"""
        try:
            # 获取最近的求职请求
            recent_requests = JobSearchRequest.objects.filter(user=user).order_by('-created_at')[:10]
            
            # 获取最近的申请记录
            recent_applications = JobApplication.objects.filter(
                job_search_request__user=user
            ).order_by('-application_time')[:20]
            
            # 计算统计数据
            total_requests = JobSearchRequest.objects.filter(user=user).count()
            total_applications = JobApplication.objects.filter(job_search_request__user=user).count()
            total_interviews = JobApplication.objects.filter(
                job_search_request__user=user,
                status__in=['contacted', 'interview']
            ).count()
            total_offers = JobApplication.objects.filter(
                job_search_request__user=user,
                status='accepted'
            ).count()
            
            # 成功率计算
            response_rate = (total_interviews / max(total_applications, 1)) * 100
            offer_rate = (total_offers / max(total_applications, 1)) * 100
            
            return {
                'total_requests': total_requests,
                'total_applications': total_applications,
                'total_interviews': total_interviews,
                'total_offers': total_offers,
                'response_rate': round(response_rate, 2),
                'offer_rate': round(offer_rate, 2),
                'recent_requests': recent_requests,
                'recent_applications': recent_applications
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'total_requests': 0,
                'total_applications': 0,
                'total_interviews': 0,
                'total_offers': 0,
                'response_rate': 0,
                'offer_rate': 0,
                'recent_requests': [],
                'recent_applications': []
            } 