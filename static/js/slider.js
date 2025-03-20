// static/js/slider.js

document.addEventListener('DOMContentLoaded', function() {
    // Swiper 슬라이더 초기화
    const initSwiper = () => {
        const swiper = new Swiper('.swiper-container', {
            // 기본 설정
            slidesPerView: 1,
            spaceBetween: 0,
            loop: true,
            speed: 800, // 슬라이드 전환 속도
            
            // 슬라이드 효과 사용
            effect: 'slide',
            
            // 슬라이드가 보이는 영역 설정 - 영역 밖으로 튀어나오지 않도록
            watchSlidesProgress: true,
            slidesOffsetBefore: 0,
            slidesOffsetAfter: 0,
            
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
                firstSlideMessage: '첫 번째 슬라이드',
                lastSlideMessage: '마지막 슬라이드',
            },
            
            // 키보드 네비게이션 활성화
            keyboard: {
                enabled: true,
                onlyInViewport: true,
            },
            
            // 터치 네비게이션 구성
            touchEventsTarget: 'container',
            touchStartPreventDefault: false, // 모바일에서 스크롤 방해 방지
        });
        
        // 슬라이더가 변경될 때 자동으로 포커스 유지
        swiper.on('slideChange', function() {
            const activeSlide = swiper.slides[swiper.activeIndex];
            const slideImg = activeSlide.querySelector('img');
            if (slideImg) {
                slideImg.setAttribute('aria-current', 'true');
            }
        });
        
        return swiper;
    };
    
    // 스와이퍼 인스턴스 초기화
    let swiperInstance = null;
    const swiperContainer = document.querySelector('.swiper-container');
    
    if (swiperContainer) {
        swiperInstance = initSwiper();
        
        // 이미지를 로드한 후 슬라이더 업데이트
        const updateSwiperAfterImagesLoaded = () => {
            const slides = document.querySelectorAll('.swiper-slide img');
            let loadedImages = 0;
            
            // 모든 이미지가 로드되면 업데이트
            const imageLoaded = () => {
                loadedImages++;
                if (loadedImages === slides.length) {
                    swiperInstance.update();
                }
            };
            
            // 각 이미지에 로드 이벤트 리스너 추가
            slides.forEach(img => {
                if (img.complete) {
                    imageLoaded();
                } else {
                    img.addEventListener('load', imageLoaded);
                    img.addEventListener('error', imageLoaded); // 이미지 오류 시에도 처리
                }
            });
        };
        
        updateSwiperAfterImagesLoaded();
        
        // 윈도우 리사이즈 시 슬라이더 업데이트
        window.addEventListener('resize', () => {
            if (swiperInstance) {
                swiperInstance.update();
            }
        });
    }
    
    // 다크 모드 토글 기능
    const initDarkMode = () => {
        const darkModeToggle = document.getElementById("dark-mode-toggle");
        const modeText = document.getElementById("mode-text");
        
        if (darkModeToggle) {
            // 사용자 선호 다크모드 체크
            const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
            const currentTheme = localStorage.getItem("darkMode");
            
            // 사용자가 이전에 테마를 설정했거나, 시스템이 다크모드를 선호하면 다크모드 적용
            if (currentTheme === "enabled" || (currentTheme === null && prefersDarkScheme.matches)) {
                document.body.classList.add("dark-mode");
                darkModeToggle.checked = true;
                if (modeText) modeText.textContent = "라이트모드";
                localStorage.setItem("darkMode", "enabled");
            }
            
            // 토글 버튼 클릭 이벤트
            darkModeToggle.addEventListener("change", function() {
                document.body.classList.toggle("dark-mode");
                
                if (document.body.classList.contains("dark-mode")) {
                    localStorage.setItem("darkMode", "enabled");
                    if (modeText) modeText.textContent = "라이트모드";
                } else {
                    localStorage.setItem("darkMode", "disabled");
                    if (modeText) modeText.textContent = "다크모드";
                }
                
                // 슬라이더 재초기화
                if (swiperInstance) {
                    swiperInstance.update();
                }
            });
            
            // 시스템 테마 변경 감지
            prefersDarkScheme.addEventListener('change', e => {
                if (!localStorage.getItem("darkMode")) { // 사용자가 직접 설정하지 않은 경우에만
                    if (e.matches) {
                        document.body.classList.add("dark-mode");
                        darkModeToggle.checked = true;
                        if (modeText) modeText.textContent = "라이트모드";
                    } else {
                        document.body.classList.remove("dark-mode");
                        darkModeToggle.checked = false;
                        if (modeText) modeText.textContent = "다크모드";
                    }
                }
            });
        }
    };
    
    // 로그인 필요 알림 기능
    const initLoginAlert = () => {
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
                    
                    // 접근성 - 모달이 열렸을 때 포커스 이동
                    const focusableElements = loginAlert.querySelectorAll('button, [tabindex]:not([tabindex="-1"])');
                    if (focusableElements.length) {
                        setTimeout(() => {
                            focusableElements[0].focus();
                        }, 100);
                    }
                });
            });
            
            // 알림 닫기 이벤트
            const closeLoginAlert = () => {
                loginAlert.style.display = 'none';
            };
            
            if (closeAlert) {
                closeAlert.addEventListener('click', closeLoginAlert);
            }
            
            if (closeAlertBtn) {
                closeAlertBtn.addEventListener('click', closeLoginAlert);
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
                    closeLoginAlert();
                }
            });
            
            // 모달 내에서 탭 키 트래핑
            loginAlert.addEventListener('keydown', function(e) {
                if (e.key === 'Tab' && loginAlert.style.display === 'flex') {
                    const focusableElements = loginAlert.querySelectorAll('button, [tabindex]:not([tabindex="-1"])');
                    const firstElement = focusableElements[0];
                    const lastElement = focusableElements[focusableElements.length - 1];
                    
                    // shift + tab
                    if (e.shiftKey) {
                        if (document.activeElement === firstElement) {
                            lastElement.focus();
                            e.preventDefault();
                        }
                    } 
                    // tab
                    else {
                        if (document.activeElement === lastElement) {
                            firstElement.focus();
                            e.preventDefault();
                        }
                    }
                }
            });
        }
    };
    
    // 플래시 메시지 처리 함수
    const handleFlashMessages = () => {
        const flashMessages = document.querySelectorAll('.flash-message');
        const container = document.getElementById('flash-messages-container');
        
        if (flashMessages.length > 0) {
            flashMessages.forEach(function(message) {
                message.classList.add('show');
                
                // 접근성 - 스크린 리더에게 알림
                message.setAttribute('role', 'alert');
                message.setAttribute('aria-live', 'assertive');
                
                // 닫기 버튼 추가
                if (!message.querySelector('.close-flash')) {
                    const closeBtn = document.createElement('button');
                    closeBtn.className = 'close-flash';
                    closeBtn.innerHTML = '&times;';
                    closeBtn.setAttribute('aria-label', '알림 닫기');
                    closeBtn.onclick = function() {
                        message.classList.remove('show');
                        setTimeout(() => {
                            if (document.body.contains(message)) {
                                message.remove();
                            }
                        }, 500);
                    };
                    
                    message.appendChild(closeBtn);
                }
                
                // 5초 후 메시지 숨기기
                setTimeout(function() {
                    if (document.body.contains(message)) {
                        message.classList.remove('show');
                        setTimeout(() => {
                            if (document.body.contains(message)) {
                                message.remove();
                            }
                        }, 500);
                    }
                }, 5000);
                
                // 컨테이너에 추가
                if (container) {
                    container.appendChild(message);
                }
            });
        }
    };
    
    // 위젯 접근성 개선
    const enhanceWidgetsAccessibility = () => {
        const widgets = document.querySelectorAll('.widget');
        widgets.forEach(widget => {
            // 위젯에 탭 인덱스 추가해 키보드 포커스 가능하게
            widget.setAttribute('tabindex', '0');
            
            // 키보드 인터랙션 처리
            widget.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    const link = this.querySelector('.widget-link');
                    if (link) {
                        e.preventDefault();
                        link.click();
                    }
                }
            });
        });
    };
    
    // 초기화 함수 실행
    initDarkMode();
    initLoginAlert();
    handleFlashMessages();
    enhanceWidgetsAccessibility();
});