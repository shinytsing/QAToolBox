from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_tarot_view(request):
    """测试塔罗牌视图"""
    return HttpResponse("塔罗牌测试页面 - 功能正常！")

@csrf_exempt
def test_api_view(request):
    """测试API视图"""
    return HttpResponse("API测试 - 功能正常！")

@csrf_exempt
def test_tarot_template_view(request):
    """测试塔罗牌模板视图"""
    try:
        return render(request, 'tools/tarot_reading.html')
    except Exception as e:
        return HttpResponse(f"模板渲染错误: {str(e)}")

@csrf_exempt
def test_tarot_reading_view(request):
    """测试塔罗牌占卜页面（无登录要求）"""
    try:
        return render(request, 'tools/tarot_reading.html')
    except Exception as e:
        return HttpResponse(f"塔罗牌页面错误: {str(e)}")

@csrf_exempt
def test_tarot_spreads_api(request):
    """测试塔罗牌阵型API（无登录要求）"""
    try:
        from ..models.tarot_models import TarotSpread
        spreads = TarotSpread.objects.filter(is_active=True)
        spreads_data = []
        for spread in spreads:
            spreads_data.append({
                'id': spread.id,
                'name': spread.name,
                'description': spread.description,
                'card_count': spread.card_count,
                'positions': spread.positions
            })
        from django.http import JsonResponse
        return JsonResponse({
            'success': True,
            'spreads': spreads_data
        })
    except Exception as e:
        from django.http import JsonResponse
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
