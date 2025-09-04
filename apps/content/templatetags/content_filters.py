"""
Content应用的模板过滤器和标签
"""

from django import template

register = template.Library()


@register.filter
def suggestion_status_display(status):
    """返回建议状态的中文显示名称"""
    displays = {"pending": "待处理", "reviewing": "审核中", "implemented": "已实现", "rejected": "已拒绝"}
    return displays.get(status, status)


@register.filter
def status_color(status):
    """返回状态对应的Bootstrap颜色类"""
    colors = {"pending": "warning", "reviewing": "info", "implemented": "success", "rejected": "danger"}
    return colors.get(status, "secondary")


@register.filter
def feedback_status_display(status):
    """返回反馈状态的中文显示名称"""
    displays = {"pending": "待处理", "processed": "已处理", "resolved": "已解决", "closed": "已关闭"}
    return displays.get(status, status)


@register.filter
def priority_display(priority):
    """返回优先级的中文显示名称"""
    displays = {"low": "低", "normal": "正常", "high": "高", "urgent": "紧急"}
    return displays.get(priority, priority)


@register.filter
def truncate_content(content, length=100):
    """截断内容到指定长度"""
    if len(content) <= length:
        return content
    return content[:length] + "..."


@register.filter
def format_datetime(dt):
    """格式化日期时间"""
    if not dt:
        return ""
    try:
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return str(dt)


@register.filter
def format_date(dt):
    """格式化日期"""
    if not dt:
        return ""
    try:
        return dt.strftime("%Y-%m-%d")
    except:
        return str(dt)
