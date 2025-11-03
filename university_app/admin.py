from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from .models import (
    Country, University, Major, Program, Criteria,
    RankingSource, Ranking, UniversityAdmissionRequirement,
    UniversityProgram
)

# Customize Admin Site
admin.site.site_header = "🎓 Quản Trị Trường Đại Học"
admin.site.site_title = "Admin Trường ĐH"
admin.site.index_title = "Chào mừng đến với Trang Quản Trị"

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'university_count')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

    def university_count(self, obj):
        count = obj.university_set.count()
        return format_html('<span style="background:#e3f2fd;padding:4px 12px;border-radius:12px;font-weight:500;color:#1976d2;">📚 {} trường</span>', count)
    university_count.short_description = 'Số trường'

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_with_icon', 'short_name', 'country_flag', 'founded_year', 'ranking_badge', 'program_count')
    list_filter = ('country', 'founded_year')
    search_fields = ('name', 'short_name', 'description')
    ordering = ('name',)
    raw_id_fields = ('country',)
    list_per_page = 25
    readonly_fields = ('created_info',)

    fieldsets = (
        ('📋 Thông Tin Cơ Bản', {
            'fields': ('name', 'short_name', 'country')
        }),
        ('📝 Mô Tả', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('📅 Thông Tin Khác', {
            'fields': ('founded_year', 'website')
        }),
    )

    def name_with_icon(self, obj):
        return format_html('🏫 <strong>{}</strong>', obj.name)
    name_with_icon.short_description = 'Tên trường'

    def country_flag(self, obj):
        if obj.country:
            return format_html('<span style="font-size:16px;">🌍</span> {}', obj.country.name)
        return '-'
    country_flag.short_description = 'Quốc gia'

    def ranking_badge(self, obj):
        ranking = obj.ranking_set.order_by('frank').first()
        if ranking:
            color = '#4caf50' if ranking.frank <= 50 else '#ff9800' if ranking.frank <= 200 else '#f44336'
            return format_html(
                '<span style="background:{};color:white;padding:4px 10px;border-radius:12px;font-weight:600;">🏆 #{}</span>',
                color, ranking.frank
            )
        return format_html('<span style="color:#9e9e9e;">Chưa xếp hạng</span>')
    ranking_badge.short_description = 'Xếp hạng'

    def program_count(self, obj):
        count = obj.universityprogram_set.count()
        return format_html('<span style="background:#e8f5e9;padding:4px 12px;border-radius:12px;font-weight:500;color:#2e7d32;">📖 {} chương trình</span>', count)
    program_count.short_description = 'Số chương trình'

    def created_info(self, obj):
        return format_html(
            '<div style="background:#f5f5f5;padding:15px;border-radius:8px;">'
            '<p><strong>ID:</strong> {}</p>'
            '<p><strong>Website:</strong> <a href="{}" target="_blank">{}</a></p>'
            '</div>',
            obj.id, obj.website or '#', obj.website or 'Chưa có'
        )
    created_info.short_description = 'Thông tin thêm'

@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_with_icon', 'program_count')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

    def name_with_icon(self, obj):
        return format_html('📚 <strong>{}</strong>', obj.name)
    name_with_icon.short_description = 'Chuyên ngành'

    def program_count(self, obj):
        count = obj.universityprogram_set.count()
        return format_html('<span style="background:#fff3e0;padding:4px 12px;border-radius:12px;font-weight:500;color:#e65100;">🎓 {} chương trình</span>', count)
    program_count.short_description = 'Số chương trình'

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_with_icon', 'level_badge')
    list_filter = ('level',)
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

    def name_with_icon(self, obj):
        return format_html('📖 <strong>{}</strong>', obj.name)
    name_with_icon.short_description = 'Tên chương trình'

    def level_badge(self, obj):
        colors = {
            'Bachelor': '#2196f3',
            'Master': '#9c27b0',
            'PhD': '#f44336',
            'Diploma': '#4caf50'
        }
        color = colors.get(obj.level, '#757575')
        return format_html('<span style="background:{};color:white;padding:4px 12px;border-radius:12px;font-weight:600;">{}</span>', color, obj.level)
    level_badge.short_description = 'Cấp độ'

@admin.register(Criteria)
class CriteriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_with_icon', 'unit_badge')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

    def name_with_icon(self, obj):
        return format_html('📊 <strong>{}</strong>', obj.name)
    name_with_icon.short_description = 'Tiêu chí'

    def unit_badge(self, obj):
        if obj.unit:
            return format_html('<span style="background:#e1f5fe;padding:4px 10px;border-radius:12px;color:#0277bd;font-weight:500;">{}</span>', obj.unit)
        return '-'
    unit_badge.short_description = 'Đơn vị'

@admin.register(RankingSource)
class RankingSourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_with_icon', 'ranking_count')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

    def name_with_icon(self, obj):
        return format_html('🏅 <strong>{}</strong>', obj.name)
    name_with_icon.short_description = 'Nguồn xếp hạng'

    def ranking_count(self, obj):
        count = obj.ranking_set.count()
        return format_html('<span style="background:#fce4ec;padding:4px 12px;border-radius:12px;font-weight:500;color:#c2185b;">📈 {} xếp hạng</span>', count)
    ranking_count.short_description = 'Số xếp hạng'

@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ('id', 'university_link', 'source_badge', 'year_badge', 'rank_badge')
    list_filter = ('fyear', 'ranking_sources')
    search_fields = ('university__name', 'ranking_sources__name')
    ordering = ('-fyear', 'frank')
    raw_id_fields = ('university', 'ranking_sources')
    list_per_page = 25

    def university_link(self, obj):
        return format_html('🏫 <strong>{}</strong>', obj.university.name)
    university_link.short_description = 'Trường'

    def source_badge(self, obj):
        return format_html('<span style="background:#e8eaf6;padding:4px 12px;border-radius:12px;color:#3f51b5;font-weight:500;">{}</span>', obj.ranking_sources.name if obj.ranking_sources else '-')
    source_badge.short_description = 'Nguồn'

    def year_badge(self, obj):
        return format_html('<span style="background:#e0f2f1;padding:4px 12px;border-radius:12px;color:#00695c;font-weight:600;">📅 {}</span>', obj.fyear)
    year_badge.short_description = 'Năm'

    def rank_badge(self, obj):
        color = '#4caf50' if obj.frank <= 50 else '#ff9800' if obj.frank <= 200 else '#f44336'
        return format_html('<span style="background:{};color:white;padding:4px 12px;border-radius:12px;font-weight:600;">🏆 #{}</span>', color, obj.frank)
    rank_badge.short_description = 'Xếp hạng'

@admin.register(UniversityAdmissionRequirement)
class UniversityAdmissionRequirementAdmin(admin.ModelAdmin):
    list_display = ('id', 'university_name', 'criteria_badge', 'value_display', 'program_name')
    list_filter = ('criteria', 'program')
    search_fields = ('university__name', 'criteria__name')
    ordering = ('id',)
    raw_id_fields = ('university', 'criteria', 'program')
    list_per_page = 25
    list_select_related = ('university', 'criteria', 'program')

    def university_name(self, obj):
        return format_html('🏫 {}', obj.university.name)
    university_name.short_description = 'Trường'

    def criteria_badge(self, obj):
        return format_html('<span style="background:#fff9c4;padding:4px 12px;border-radius:12px;color:#f57f17;font-weight:500;">{}</span>', obj.criteria.name if obj.criteria else '-')
    criteria_badge.short_description = 'Tiêu chí'

    def value_display(self, obj):
        return format_html('<strong style="color:#1976d2;">{}</strong>', obj.value)
    value_display.short_description = 'Giá trị'

    def program_name(self, obj):
        return obj.program.name if obj.program else '-'
    program_name.short_description = 'Chương trình'

@admin.register(UniversityProgram)
class UniversityProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'university_name', 'program_badge', 'major_name', 'tuition_display', 'duration_badge')
    list_filter = ('program', 'major')
    search_fields = ('university__name', 'major__name', 'program__name')
    ordering = ('id',)
    raw_id_fields = ('university', 'program', 'major')
    list_per_page = 25
    list_select_related = ('university', 'program', 'major')

    def university_name(self, obj):
        return format_html('🏫 {}', obj.university.name)
    university_name.short_description = 'Trường'

    def program_badge(self, obj):
        return format_html('<span style="background:#e3f2fd;padding:4px 12px;border-radius:12px;color:#1565c0;font-weight:500;">{}</span>', obj.program.name if obj.program else '-')
    program_badge.short_description = 'Chương trình'

    def major_name(self, obj):
        return format_html('📚 {}', obj.major.name if obj.major else '-')
    major_name.short_description = 'Chuyên ngành'

    def tuition_display(self, obj):
        if obj.tuition_fee:
            return format_html('<span style="background:#e8f5e9;padding:4px 12px;border-radius:12px;color:#2e7d32;font-weight:600;">💰 ${:,.0f}/năm</span>', obj.tuition_fee)
        return '-'
    tuition_display.short_description = 'Học phí'

    def duration_badge(self, obj):
        if obj.duration:
            return format_html('<span style="background:#fce4ec;padding:4px 12px;border-radius:12px;color:#c2185b;font-weight:500;">⏱️ {} năm</span>', obj.duration)
        return '-'
    duration_badge.short_description = 'Thời gian' 
