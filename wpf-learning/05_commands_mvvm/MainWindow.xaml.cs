// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WPF 05 - MVVM (Code-Behind)                         ■
// ■  View의 코드비하인드는 최소한으로 유지합니다            ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
//
// MVVM에서 Code-Behind는 거의 비어있습니다!
// 모든 로직은 ViewModel에 있기 때문입니다.
// 레스토랑에서 테이블(View)은 그냥 자리만 제공하고,
// 주문과 서빙은 웨이터(ViewModel)가 합니다.

using System.Windows;

namespace LessonWpf
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            // DataContext는 XAML에서 설정했으므로 여기서 할 일이 없습니다.
            // MVVM의 장점: Code-Behind가 깔끔합니다!
        }
    }
}
