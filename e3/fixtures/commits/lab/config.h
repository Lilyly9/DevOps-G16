#ifndef CONFIG_H
#define CONFIG_H

/* 项目头文件提供的基础值。 */
#define BASE 10

/* 构建模式：默认 0，C2 用 -DMODE=7 在编译命令里覆盖。 */
#ifndef MODE
#define MODE 0
#endif

#endif /* CONFIG_H */
