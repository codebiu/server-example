import org.apache.commons.lang3.StringUtils;

public class HelloWorld {
    public static void main(String[] args) {
        // 使用 Apache Commons Lang 的 StringUtils 类来检查字符串是否为空白
        String message = "Hello, World!";
        if (StringUtils.isNotBlank(message)) {
            System.out.println(message);
        }
    }
}