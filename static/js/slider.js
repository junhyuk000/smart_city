document.addEventListener('DOMContentLoaded', function() {
    // Swiper 슬라이더 초기화
    const swiper = new Swiper('.swiper-container', {
        // 기본 설정
        slidesPerView: 1,
        spaceBetween: 0,
        loop: true,
        speed: 800, // 슬라이드 전환 속도 조정
        
        // 페이드 효과 제거하고 슬라이드 효과 사용
        effect: 'slide',
        
        // 자동 재생 설정
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
        
        // 네비게이션 버튼 설정
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        
        // 페이지네이션 설정
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        
        // 오버플로우 처리
        watchOverflow: true,
        
        // 슬라이더가 화면 밖으로 나가지 않도록 설정
        observer: true,
        observeParents: true,
        
        // 슬라이드 효과를 더 부드럽게 만들기 위한 설정
        grabCursor: true,
        touchRatio: 1,
        touchAngle: 45,
        simulateTouch: true,
        
        // 접근성 개선
        a11y: {
            prevSlideMessage: '이전 슬라이드',
            nextSlideMessage: '다음 슬라이드',
            paginationBulletMessage: '{{index}}번 슬라이드로 이동',
        }
    });
    
    // 다크 모드 토글 기능
    const darkModeToggle = document.getElementById("dark-mode-toggle");
    const modeText = document.getElementById("mode-text");
    
    if (darkModeToggle) {
        darkModeToggle.addEventListener("change", function() {
            document.body.classList.toggle("dark-mode");
            
            if (document.body.classList.contains("dark-mode")) {
                localStorage.setItem("darkMode", "enabled");
                if (modeText) modeText.textContent = "라이트모드";
            } else {
                localStorage.setItem("darkMode", "disabled");
                if (modeText) modeText.textContent = "다크모드";
            }
        });
        
        // 페이지 로드 시 다크모드 설정 유지
        if (localStorage.getItem("darkMode") === "enabled") {
            document.body.classList.add("dark-mode");
            darkModeToggle.checked = true;
            if (modeText) modeText.textContent = "라이트모드";
        }
    }
    
    // 로그인 필요 알림 기능
    const loginRequiredLinks = document.querySelectorAll('.login-required');
    const loginAlert = document.getElementById('login-alert');
    
    if (loginRequiredLinks.length > 0 && loginAlert) {
        const closeAlert = document.querySelector('.close-alert');
        const goToLogin = document.getElementById('go-to-login');
        const closeAlertBtn = document.getElementById('close-alert-btn');
        
        // 로그인 필요 링크 클릭 이벤트
        loginRequiredLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                loginAlert.style.display = 'flex';
            });
        });
        
        // 알림 닫기 이벤트
        if (closeAlert) {
            closeAlert.addEventListener('click', function() {
                loginAlert.style.display = 'none';
            });
        }
        
        if (closeAlertBtn) {
            closeAlertBtn.addEventListener('click', function() {
                loginAlert.style.display = 'none';
            });
        }
        
        // 로그인 페이지로 이동 이벤트
        if (goToLogin) {
            goToLogin.addEventListener('click', function() {
                window.location.href = "/login";
            });
        }
        
        // ESC 키로 알림 닫기
        window.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && loginAlert.style.display === 'flex') {
                loginAlert.style.display = 'none';
            }
        });
    }
    
    // 플래시 메시지 처리 함수
    function handleFlashMessages() {
        const flashMessages = document.querySelectorAll('.flash-message');
        const container = document.getElementById('flash-messages-container');
        
        if (flashMessages.length > 0) {
            flashMessages.forEach(function(message) {
                message.classList.add('show');
                
                // 닫기 버튼 추가
                if (!message.querySelector('.close-flash')) {
                    const closeBtn = document.createElement('button');
                    closeBtn.className = 'close-flash';
                    closeBtn.innerHTML = '&times;';
                    closeBtn.setAttribute('aria-label', '알림 닫기');
                    closeBtn.onclick = function() {
                        message.classList.remove('show');
                        setTimeout(() => message.remove(), 500);
                    };
                    
                    message.appendChild(closeBtn);
                }
                
                // 5초 후 메시지 숨기기
                setTimeout(function() {
                    if (document.body.contains(message)) {
                        message.classList.remove('show');
                        setTimeout(() => message.remove(), 500);
                    }
                }, 5000);
                
                // 컨테이너에 추가
                if (container) {
                    container.appendChild(message);
                }
            });
        }
    }
    
    // 페이지 로드 시 Flash 메시지 처리
    handleFlashMessages();
    
    // 위젯 접근성 개선 - 키보드 포커스 처리
    const widgets = document.querySelectorAll('.widget');
    widgets.forEach(widget => {
        widget.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const link = this.querySelector('.widget-link');
                if (link) link.click();
            }
        });
    });
});