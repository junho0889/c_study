// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WPF 04 - 스타일과 템플릿 (Code-Behind)               ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;

namespace LessonWpf
{
    // ┌──────────────────────────────────────────────────┐
    // │  색상 데이터 클래스 - DataTemplate에서 사용       │
    // └──────────────────────────────────────────────────┘
    // DataTemplate이 이 클래스의 속성(Name, Color)을 읽어서
    // 화면에 표시합니다. 이력서 양식에 이름, 사진을 넣는 것처럼!
    public class ColorItem
    {
        public string Name { get; set; } = "";
        public string Color { get; set; } = "";
    }

    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            LoadColorData();
        }

        // ┌──────────────────────────────────────────┐
        // │  DataTemplate용 색상 데이터 로드           │
        // └──────────────────────────────────────────┘
        private void LoadColorData()
        {
            // 이 데이터가 DataTemplate에 의해 "색상 사각형 + 이름" 형태로 표시됩니다.
            var colors = new List<ColorItem>
            {
                new ColorItem { Name = "빨강 (Red)", Color = "#FFE53935" },
                new ColorItem { Name = "파랑 (Blue)", Color = "#FF1E88E5" },
                new ColorItem { Name = "초록 (Green)", Color = "#FF43A047" },
                new ColorItem { Name = "주황 (Orange)", Color = "#FFFB8C00" },
                new ColorItem { Name = "보라 (Purple)", Color = "#FF8E24AA" },
                new ColorItem { Name = "청록 (Teal)", Color = "#FF00897B" },
                new ColorItem { Name = "분홍 (Pink)", Color = "#FFD81B60" },
                new ColorItem { Name = "회색 (Gray)", Color = "#FF757575" }
            };

            ColorList.ItemsSource = colors;
        }

        // ┌──────────────────────────────────────────┐
        // │  버튼 클릭 이벤트                         │
        // └──────────────────────────────────────────┘
        private void OnButtonClick(object sender, RoutedEventArgs e)
        {
            if (sender is Button button)
            {
                string styleName = "기본";
                if (button.Style != null)
                {
                    // 어떤 스타일이 적용되었는지 확인
                    if (button.Style == (Style)Resources["BlueButtonStyle"])
                        styleName = "BlueButtonStyle";
                    else if (button.Style == (Style)Resources["GreenButtonStyle"])
                        styleName = "GreenButtonStyle";
                    else if (button.Style == (Style)Resources["DangerButtonStyle"])
                        styleName = "DangerButtonStyle";
                    else if (button.Style == (Style)Resources["RoundButtonStyle"])
                        styleName = "RoundButtonStyle (ControlTemplate)";
                }

                ResultText.Text =
                    $"클릭된 버튼: '{button.Content}'\n" +
                    $"적용된 스타일: {styleName}\n" +
                    $"Style은 XAML에서 정의하고, 여러 버튼이 같은 스타일을 공유합니다.\n" +
                    $"Trigger로 마우스를 올리면 색이 변하고, IsEnabled=False면 회색이 됩니다.";
            }
        }
    }
}
