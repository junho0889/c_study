// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WPF 07 - DetailPage Code-Behind                     ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

using System.Windows;
using System.Windows.Controls;

namespace LessonWpf
{
    public partial class DetailPage : Page
    {
        private readonly MainWindow _mainWindow;

        public DetailPage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;

            // 이전 데이터 복원
            PhoneBox.Text = mainWindow.SharedData.Phone;
            HobbyBox.Text = mainWindow.SharedData.Hobby;
            AgreeCheck.IsChecked = mainWindow.SharedData.AgreeTerms;
        }

        // ┌──────────────────────────────────────────┐
        // │  이전 페이지로 돌아가기                    │
        // └──────────────────────────────────────────┘
        // GoBack()은 브라우저의 "뒤로" 버튼과 같습니다.
        // 이전에 보던 페이지로 돌아갑니다.
        private void OnBack(object sender, RoutedEventArgs e)
        {
            SaveData();
            _mainWindow.GoBack();
        }

        // ┌──────────────────────────────────────────┐
        // │  완료 페이지로 이동                        │
        // └──────────────────────────────────────────┘
        private void OnComplete(object sender, RoutedEventArgs e)
        {
            SaveData();
            _mainWindow.GoToComplete();
        }

        private void SaveData()
        {
            _mainWindow.SharedData.Phone = PhoneBox.Text;
            _mainWindow.SharedData.Hobby = HobbyBox.Text;
            _mainWindow.SharedData.AgreeTerms = AgreeCheck.IsChecked ?? false;
        }
    }
}
