// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WPF 09 - RatingControl (커스텀 별점 컨트롤)          ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
//
// 이 파일은 별점(Star Rating) 컨트롤을 직접 만드는 예제입니다.
// UserControl을 상속받아서 기존 컨트롤(TextBlock)을 조합합니다.
//
// 핵심 개념:
//   DependencyProperty = WPF의 특별한 속성
//     - 일반 C# 속성: 값을 저장만 합니다.
//     - DependencyProperty: 바인딩, 애니메이션, 스타일이 가능합니다!
//     - 등기 우편(추적 가능) vs 일반 우편(추적 불가)
//
//   RoutedEvent = 이벤트가 부모에게 전달
//     - 일반 이벤트: 발생한 곳에서만 처리
//     - RoutedEvent: 자식 → 부모로 전달 (소리가 퍼지듯)
//     - 교실에서 학생이 소리치면 복도까지 들리는 것!

using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;

namespace LessonWpf
{
    // ┌──────────────────────────────────────────────────┐
    // │  RatingControl - 별점 평가 UserControl            │
    // └──────────────────────────────────────────────────┘
    public class RatingControl : UserControl
    {
        private readonly StackPanel _starPanel;

        // ┌──────────────────────────────────────────┐
        // │  DependencyProperty 정의                  │
        // └──────────────────────────────────────────┘
        // DependencyProperty는 3단계로 만듭니다:
        //   1) DependencyProperty.Register()로 등록
        //   2) CLR 래퍼 속성 만들기 (get/set)
        //   3) PropertyChangedCallback으로 변경 시 동작 정의

        // ── Rating 속성 (현재 별점) ──
        // 이 속성은 XAML에서 바인딩할 수 있고,
        // 값이 바뀌면 자동으로 별 모양이 업데이트됩니다.
        public static readonly DependencyProperty RatingProperty =
            DependencyProperty.Register(
                nameof(Rating),           // 속성 이름
                typeof(int),              // 속성 타입
                typeof(RatingControl),    // 소유자 타입
                new PropertyMetadata(0, OnRatingChanged)); // 기본값 + 변경 콜백

        public int Rating
        {
            get => (int)GetValue(RatingProperty);
            set => SetValue(RatingProperty, value);
        }

        // ── MaxRating 속성 (최대 별 개수) ──
        public static readonly DependencyProperty MaxRatingProperty =
            DependencyProperty.Register(
                nameof(MaxRating), typeof(int), typeof(RatingControl),
                new PropertyMetadata(5, OnMaxRatingChanged));

        public int MaxRating
        {
            get => (int)GetValue(MaxRatingProperty);
            set => SetValue(MaxRatingProperty, value);
        }

        // ── StarSize 속성 (별 크기) ──
        public static readonly DependencyProperty StarSizeProperty =
            DependencyProperty.Register(
                nameof(StarSize), typeof(double), typeof(RatingControl),
                new PropertyMetadata(30.0, OnAppearanceChanged));

        public double StarSize
        {
            get => (double)GetValue(StarSizeProperty);
            set => SetValue(StarSizeProperty, value);
        }

        // ── ActiveColor 속성 (선택된 별 색상) ──
        public static readonly DependencyProperty ActiveColorProperty =
            DependencyProperty.Register(
                nameof(ActiveColor), typeof(string), typeof(RatingControl),
                new PropertyMetadata("#FFFFC107", OnAppearanceChanged));

        public string ActiveColor
        {
            get => (string)GetValue(ActiveColorProperty);
            set => SetValue(ActiveColorProperty, value);
        }

        // ── InactiveColor 속성 (비선택 별 색상) ──
        public static readonly DependencyProperty InactiveColorProperty =
            DependencyProperty.Register(
                nameof(InactiveColor), typeof(string), typeof(RatingControl),
                new PropertyMetadata("#FFE0E0E0", OnAppearanceChanged));

        public string InactiveColor
        {
            get => (string)GetValue(InactiveColorProperty);
            set => SetValue(InactiveColorProperty, value);
        }

        // ┌──────────────────────────────────────────┐
        // │  RoutedEvent 정의                         │
        // └──────────────────────────────────────────┘
        // RoutedEvent는 이벤트가 자식에서 부모로 전달됩니다.
        // RoutingStrategy.Bubble = 거품처럼 위로 올라감
        // 교실(컨트롤)에서 시작된 소리가 복도(Window)까지 들리는 것!
        public static readonly RoutedEvent RatingChangedEvent =
            EventManager.RegisterRoutedEvent(
                "RatingChanged",              // 이벤트 이름
                RoutingStrategy.Bubble,       // 버블링: 자식 → 부모로 전달
                typeof(RoutedEventHandler),   // 핸들러 타입
                typeof(RatingControl));       // 소유자

        // CLR 이벤트 래퍼 (XAML에서 RatingChanged="..." 사용 가능)
        public event RoutedEventHandler RatingChanged
        {
            add => AddHandler(RatingChangedEvent, value);
            remove => RemoveHandler(RatingChangedEvent, value);
        }

        // ┌──────────────────────────────────────────┐
        // │  생성자 - 별 모양 초기화                   │
        // └──────────────────────────────────────────┘
        public RatingControl()
        {
            _starPanel = new StackPanel
            {
                Orientation = Orientation.Horizontal
            };
            Content = _starPanel;

            Loaded += (s, e) => BuildStars();
        }

        // ┌──────────────────────────────────────────┐
        // │  별 생성 및 업데이트                       │
        // └──────────────────────────────────────────┘
        private void BuildStars()
        {
            _starPanel.Children.Clear();

            for (int i = 1; i <= MaxRating; i++)
            {
                int starIndex = i; // 클로저 캡처용

                var star = new TextBlock
                {
                    Text = "\u2605",  // ★ 별 유니코드 문자
                    FontSize = StarSize,
                    Cursor = Cursors.Hand,
                    Margin = new Thickness(2, 0, 2, 0),
                    Tag = starIndex   // 몇 번째 별인지 태그에 저장
                };

                // 마우스 클릭 이벤트
                star.MouseLeftButtonDown += (s, e) =>
                {
                    Rating = starIndex;
                    // RoutedEvent 발생! (소리가 퍼지듯 부모에게 전달)
                    RaiseEvent(new RoutedEventArgs(RatingChangedEvent));
                };

                // 마우스 호버: 미리보기 효과
                star.MouseEnter += (s, e) => PreviewRating(starIndex);
                star.MouseLeave += (s, e) => UpdateStarColors();

                _starPanel.Children.Add(star);
            }

            UpdateStarColors();
        }

        // ── 별 색상 업데이트 ──
        private void UpdateStarColors()
        {
            var activeBrush = new BrushConverter().ConvertFromString(ActiveColor) as Brush
                              ?? Brushes.Gold;
            var inactiveBrush = new BrushConverter().ConvertFromString(InactiveColor) as Brush
                                ?? Brushes.LightGray;

            for (int i = 0; i < _starPanel.Children.Count; i++)
            {
                if (_starPanel.Children[i] is TextBlock star)
                {
                    star.Foreground = (i < Rating) ? activeBrush : inactiveBrush;
                    star.FontSize = StarSize;
                }
            }
        }

        // ── 마우스 호버 미리보기 ──
        private void PreviewRating(int previewValue)
        {
            var activeBrush = new BrushConverter().ConvertFromString(ActiveColor) as Brush
                              ?? Brushes.Gold;
            var inactiveBrush = new BrushConverter().ConvertFromString(InactiveColor) as Brush
                                ?? Brushes.LightGray;

            for (int i = 0; i < _starPanel.Children.Count; i++)
            {
                if (_starPanel.Children[i] is TextBlock star)
                {
                    star.Foreground = (i < previewValue) ? activeBrush : inactiveBrush;
                }
            }
        }

        // ── DependencyProperty 변경 콜백 ──
        // 속성 값이 바뀌면 자동으로 호출되는 메서드입니다.
        // 감시 카메라가 변화를 감지하면 알람을 울리는 것과 같아요!
        private static void OnRatingChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is RatingControl control)
                control.UpdateStarColors();
        }

        private static void OnMaxRatingChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is RatingControl control && control.IsLoaded)
                control.BuildStars();
        }

        private static void OnAppearanceChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is RatingControl control && control.IsLoaded)
                control.UpdateStarColors();
        }
    }
}
