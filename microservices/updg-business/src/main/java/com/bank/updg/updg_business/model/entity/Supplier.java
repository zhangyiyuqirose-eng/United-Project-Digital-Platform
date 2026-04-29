package com.bank.updg.updg_business.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_supplier")
public class Supplier {
    @TableId
    private String supplierId;
    private String supplierCode;
    private String supplierName;
    private String contactPerson;
    private String contactPhone;
    private String contactEmail;
    private String type;
    private String rating;
    private String status;
    private String qualifications;
    private String address;
    private String createTime;
    private String updateTime;
}
