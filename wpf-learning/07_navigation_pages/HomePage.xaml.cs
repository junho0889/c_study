// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WPF 07 - HomePage Code-Behind                       ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

using System.Windows;
using System.Windows.Controls;

namespace LessonWpf
{
    public partial class HomePage : Page
    {
        private readonly MainWindow _mainWindow;

        // ┌──────────────────────────────────────────┐
        // │  페이지 간 데이터 전달                     │
        // └──────────────────────────────────────────┘
        // 생성자에서 MainWindow를 받아서 SharedData에 접근합니다.
        // 편지봉투(MainWindow)를 받아서 안의 편지(SharedData)를 읽는 것!
        public HomePage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;

            // 이전에 입력한 데이터가 있으면 복원
            NameBox.Text = mainWindow.SharedData.Name;
            EmailBox.Text = mainWindow.SharedData.Email;
        }

        // ┌──────────────────────────────────────────┐
        // │  다음 페이지로 이동                        │
        // └──────────────────────────────────────────┘
        private void OnNext(object sender, RoutedEventArgs e)
        {
            // 데이터 저장 (여행 가방에 짐 넣기)
            _mainWindow.SharedData.Name = NameBox.Text;
            _mainWindow.SharedData.Email = EmailBox.Text;

            // 다음 페이지로 이동 (채널 변경!)
            _mainWindow.GoToDetail();
        }
    }
}
