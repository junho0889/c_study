// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WPF 08 - 리소스와 애니메이션 (Code-Behind)            ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Animation;

namespace LessonWpf
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }

        // ┌──────────────────────────────────────────┐
        // │  DynamicResource 테마 변경                 │
        // └──────────────────────────────────────────┘
        // DynamicResource는 "바꿀 수 있는 물감"입니다.
        // Resources["키"] = 새 값 으로 런타임에 변경하면
        // DynamicResource로 연결된 모든 컨트롤이 자동 업데이트!
        //
        // StaticResource는 처음 한 번만 읽고 끝이라 바꿀 수 없고,
        // DynamicResource는 나중에도 바꿀 수 있습니다.
        // 사진을 인쇄(Static) vs 모니터에 표시(Dynamic)

        private void OnBlueTheme(object sender, RoutedEventArgs e)
        {
            Resources["PrimaryColor"] = new SolidColorBrush(
                (Color)ColorConverter.ConvertFromString("#FF3F51B5"));
        }

        private void OnGreenTheme(object sender, RoutedEventArgs e)
        {
            Resources["PrimaryColor"] = new SolidColorBrush(
                (Color)ColorConverter.ConvertFromString("#FF4CAF50"));
        }

        private void OnOrangeTheme(object sender, RoutedEventArgs e)
        {
            Resources["PrimaryColor"] = new SolidColorBrush(
                (Color)ColorConverter.ConvertFromString("#FFFF9800"));
        }

        // ┌──────────────────────────────────────────┐
        // │  Storyboard 제어                          │
        // └──────────────────────────────────────────┘
        // Storyboard는 XAML에서 정의한 애니메이션 대본입니다.
        // Begin() = "액션!" (촬영 시작)
        // Stop()  = "컷!" (촬영 중지)

        private void OnStartAll(object sender, RoutedEventArgs e)
        {
            // FindResource로 XAML에 정의된 Storyboard를 찾아서 실행
            // 감독이 대본을 찾아서 "촬영 시작!" 하는 것과 같아요!
            ((Storyboard)FindResource("SlideAnimation")).Begin();
            ((Storyboard)FindResource("PulseAnimation")).Begin();
            ((Storyboard)FindResource("ColorAnimation")).Begin();
            ((Storyboard)FindResource("RotateAnimation")).Begin();
            ((Storyboard)FindResource("FadeAnimation")).Begin();
        }

        private void OnStopAll(object sender, RoutedEventArgs e)
        {
            ((Storyboard)FindResource("SlideAnimation")).Stop();
            ((Storyboard)FindResource("PulseAnimation")).Stop();
            ((Storyboard)FindResource("ColorAnimation")).Stop();
            ((Storyboard)FindResource("RotateAnimation")).Stop();
            ((Storyboard)FindResource("FadeAnimation")).Stop();
        }
    }
}
