// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WPF 07 - 네비게이션 (Code-Behind)                    ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

using System.Windows;
using System.Windows.Navigation;

namespace LessonWpf
{
    // ┌──────────────────────────────────────────────────┐
    // │  회원가입 데이터 - 페이지 간 전달용                │
    // └──────────────────────────────────────────────────┘
    // 모든 페이지가 공유하는 데이터 객체입니다.
    // 여행 가방처럼 페이지를 이동할 때 같이 가져갑니다!
    public class RegistrationData
    {
        public string Name { get; set; } = "";
        public string Email { get; set; } = "";
        public string Phone { get; set; } = "";
        public string Hobby { get; set; } = "";
        public bool AgreeTerms { get; set; }
    }

    public partial class MainWindow : Window
    {
        // ┌──────────────────────────────────────────┐
        // │  공유 데이터 - 모든 페이지가 접근 가능     │
        // └──────────────────────────────────────────┘
        public RegistrationData SharedData { get; } = new();

        public MainWindow()
        {
            InitializeComponent();

            // 첫 번째 페이지로 이동
            // Frame.Navigate()는 리모컨으로 채널을 바꾸는 것!
            MainFrame.Navigate(new HomePage(this));
        }

        // ┌──────────────────────────────────────────┐
        // │  페이지 전환 시 단계 표시 업데이트          │
        // └──────────────────────────────────────────┘
        private void MainFrame_Navigated(object sender, NavigationEventArgs e)
        {
            // 현재 페이지가 무엇인지 확인해서 단계를 표시합니다.
            string step = e.Content switch
            {
                HomePage => "1단계 / 3단계: 기본 정보",
                DetailPage => "2단계 / 3단계: 추가 정보",
                CompletePage => "3단계 / 3단계: 완료!",
                _ => ""
            };
            StepIndicator.Text = step;
        }

        // ── 페이지 이동 도우미 메서드 ──
        public void GoToDetail() => MainFrame.Navigate(new DetailPage(this));
        public void GoToComplete() => MainFrame.Navigate(new CompletePage(this));
        public void GoToHome()
        {
            // 뒤로가기 기록 모두 지우기
            while (MainFrame.CanGoBack)
                MainFrame.RemoveBackEntry();
            MainFrame.Navigate(new HomePage(this));
        }
        public void GoBack()
        {
            if (MainFrame.CanGoBack)
                MainFrame.GoBack();
        }
    }

    // ┌──────────────────────────────────────────────────┐
    // │  완료 페이지 (XAML 없이 코드로만 만든 Page)       │
    // └──────────────────────────────────────────────────┘
    // Page는 XAML 없이 코드로만 만들 수도 있습니다.
    // 간단한 페이지는 이렇게 만들면 편합니다!
    public class CompletePage : System.Windows.Controls.Page
    {
        public CompletePage(MainWindow mainWindow)
        {
            var data = mainWindow.SharedData;

            var panel = new System.Windows.Controls.StackPanel
            {
                Margin = new Thickness(25)
            };

            panel.Children.Add(new System.Windows.Controls.TextBlock
            {
                Text = "회원가입 완료!",
                FontSize = 24,
                FontWeight = FontWeights.Bold,
                Margin = new Thickness(0, 0, 0, 20)
            });

            // 입력된 정보 표시
            var info =
                $"이름: {data.Name}\n" +
                $"이메일: {data.Email}\n" +
                $"전화번호: {data.Phone}\n" +
                $"취미: {data.Hobby}\n" +
                $"약관 동의: {(data.AgreeTerms ? "동의함" : "동의하지 않음")}";

            var border = new System.Windows.Controls.Border
            {
                Padding = new Thickness(15),
                Background = System.Windows.Media.Brushes.AliceBlue,
                CornerRadius = new CornerRadius(8),
                Margin = new Thickness(0, 0, 0, 20)
            };
            border.Child = new System.Windows.Controls.TextBlock
            {
                Text = info,
                FontSize = 14,
                LineHeight = 24
            };
            panel.Children.Add(border);

            var homeBtn = new System.Windows.Controls.Button
            {
                Content = "처음으로",
                Padding = new Thickness(25, 10, 25, 10),
                FontSize = 14
            };
            homeBtn.Click += (s, e) => mainWindow.GoToHome();
            panel.Children.Add(homeBtn);

            Content = panel;
        }
    }
}
