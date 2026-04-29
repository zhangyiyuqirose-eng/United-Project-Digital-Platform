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
@TableName("pm_customer")
public class Customer {
    @TableId
    private String customerId;
    private String name;
    private String type;
    private String industry;
    private String contactPerson;
    private String phone;
    private String email;
    private String address;
    private String creditCode;
    private String rating;
    private String status;
    private String notes;
    private String createdAt;
    private String updatedAt;
}
