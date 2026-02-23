# 配置文件说明

本项目中，配置文件分三种，分别是：默认配置、生产配置和实例配置。

**优先级**：实例配置 > 生产配置>  默认配置。

## 默认配置

**保存位置**：`config/default.json`

作用：包含所有可能用到的设置项，是项目的完整模板。

## 生产配置

**保存位置**：`config/product.json`

**作用**：预设的生产环境专用值（如关闭调试模式）

本文件可不包含全部配置项，仅包含生产环境需要修改的。

## 实例配置

保存位置：`user/config.json`

作用：实际使用时的真实数据值，在真正部署时使用。在`.gitignore`中。



# 使用说明

开发时，需要添加新的设置项，改`default.json`；

测试真实数据（如真实的店名，真实打印机数据），改`user/config.json`；

部署到服务器`product.json`及`user/config.json`。



# 加载顺序

靠后加载的覆盖前面已有的。

1. `config/default.json`
2. `conifg/product.json`（仅环境变量`ENVIRONMENT=production`时加载）
3. `user/conifg.json`

# 生产模式

通过环境变量`ENVIRONMENT`判断。

