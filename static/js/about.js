// static/js/about.js

document.addEventListener('DOMContentLoaded', function() {
    // 섹션 애니메이션 효과
    const sections = document.querySelectorAll('.about-section');
    
    // 스크롤 시 애니메이션 적용
    function checkSections() {
        const triggerBottom = window.innerHeight * 0.8;
        
        sections.forEach(section => {
            const sectionTop = section.getBoundingClientRect().top;
            
            if (sectionTop < triggerBottom) {
                section.style.opacity = '1';
                section.style.transform = 'translateY(0)';
            }
        });
    }
    
    // 초기 상태 설정
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    });
    
    // 페이지 로드 시 및 스크롤 시 섹션 확인
    window.addEventListener('load', checkSections);
    window.addEventListener('scroll', checkSections);
    
    // 팀 멤버 마우스오버 효과
    const teamMembers = document.querySelectorAll('.team-member');
    
    teamMembers.forEach(member => {
        member.addEventListener('mouseenter', function() {
            this.querySelector('.member-avatar').style.backgroundColor = '#218838';
        });
        
        member.addEventListener('mouseleave', function() {
            this.querySelector('.member-avatar').style.backgroundColor = '';
        });
    });
});