// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WPF 09 - 커스텀 컨트롤 (Code-Behind)                 ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

using System.Windows;

namespace LessonWpf
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }

        // ┌──────────────────────────────────────────┐
        // │  RatingChanged 이벤트 핸들러              │
        // └──────────────────────────────────────────┘
        // RatingControl에서 별을 클릭하면 이 메서드가 호출됩니다.
        // RoutedEvent가 자식(별)에서 부모(Window)까지 전달됩니다!
        // 교실에서 학생이 손을 들면 선생님이 보는 것과 같아요.
        private void OnRatingChanged(object sender, RoutedEventArgs e)
        {
            if (sender is RatingControl control)
            {
                string name = control.Name;
                int rating = control.Rating;
                int max = control.MaxRating;

                string emoji = rating switch
                {
                    <= 1 => "아쉬워요",
                    <= 3 => "보통이에요",
                    <= 4 => "좋아요",
                    _ => "최고예요!"
                };

                ResultText.Text =
                    $"[{name}] 평가: {rating} / {max} - {emoji}\n" +
                    $"별 크기: {control.StarSize}px\n" +
                    $"이 이벤트는 RatingControl 내부에서 발생하여\n" +
                    $"RoutedEvent를 통해 MainWindow까지 전달되었습니다.";
            }
        }
    }
}
